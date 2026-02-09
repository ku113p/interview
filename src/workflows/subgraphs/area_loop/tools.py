"""Area loop tools, schemas, and tool registry."""

import logging
import uuid
from typing import Annotated

import aiosqlite
from langchain.tools import tool
from langchain_core.messages.tool import ToolCall
from pydantic import AfterValidator, BaseModel, Field

from src.infrastructure.db import managers as db

from .methods import CriteriaMethods, CurrentAreaMethods, LifeAreaMethods

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# UUID Validation
# -----------------------------------------------------------------------------


def _validate_uuid(value: str) -> str:
    """Validate that a string is a valid UUID format."""
    try:
        uuid.UUID(value)
    except ValueError as exc:
        logger.warning("Invalid UUID input", extra={"value": value})
        raise ValueError(f"Invalid UUID: {value}") from exc
    return value


UUIDStr = Annotated[str, AfterValidator(_validate_uuid)]


# -----------------------------------------------------------------------------
# Argument Schemas
# -----------------------------------------------------------------------------


class ListLifeAreasArgs(BaseModel):
    """Arguments for listing life areas."""

    user_id: UUIDStr = Field(
        ..., description="UUID of the user (provided in system message)"
    )


class GetLifeAreaArgs(BaseModel):
    """Arguments for getting a single life area."""

    user_id: UUIDStr = Field(
        ..., description="UUID of the user (provided in system message)"
    )
    area_id: UUIDStr = Field(..., description="UUID of the life area to fetch")


class CreateLifeAreaArgs(BaseModel):
    """Arguments for creating a life area."""

    user_id: UUIDStr = Field(
        ..., description="UUID of the user (provided in system message)"
    )
    title: str = Field(..., description="Title/name for the new life area")
    parent_id: UUIDStr | None = Field(
        None,
        description="Optional UUID of parent life area for hierarchical organization",
    )


class DeleteLifeAreaArgs(BaseModel):
    """Arguments for deleting a life area."""

    user_id: UUIDStr = Field(
        ..., description="UUID of the user (provided in system message)"
    )
    area_id: UUIDStr = Field(..., description="UUID of the life area to delete")


class ListCriteriaArgs(BaseModel):
    """Arguments for listing criteria."""

    user_id: UUIDStr = Field(
        ..., description="UUID of the user (provided in system message)"
    )
    area_id: UUIDStr = Field(
        ...,
        description="UUID of the life area. Use 'list_life_areas' first if you don't have the ID.",
    )


class CreateCriteriaArgs(BaseModel):
    """Arguments for creating a criteria item."""

    user_id: UUIDStr = Field(
        ..., description="UUID of the user (provided in system message)"
    )
    area_id: UUIDStr = Field(
        ...,
        description="UUID of the life area. Call 'list_life_areas' to get available area IDs, then extract the 'id' field from the response.",
    )
    title: str = Field(..., description="Title/name for the new criteria item")


class DeleteCriteriaArgs(BaseModel):
    """Arguments for deleting a criteria item."""

    user_id: UUIDStr = Field(
        ..., description="UUID of the user (provided in system message)"
    )
    criteria_id: UUIDStr = Field(..., description="UUID of the criteria item to delete")


class SetCurrentAreaArgs(BaseModel):
    """Arguments for setting the current area for interview."""

    user_id: UUIDStr = Field(
        ..., description="UUID of the user (provided in system message)"
    )
    area_id: UUIDStr = Field(
        ...,
        description="UUID of the life area to set as current for interview",
    )


# -----------------------------------------------------------------------------
# Tool Calling
# -----------------------------------------------------------------------------


async def call_tool(tool_call: ToolCall, conn: aiosqlite.Connection | None = None):
    """Execute a tool call by name with given arguments."""
    tool_name = tool_call["name"]
    tool_args = dict(tool_call.get("args", {}) or {})
    tool_args.pop("conn", None)

    tool_fn = TOOL_METHODS.get(tool_name)

    if tool_fn is None:
        raise KeyError(f"Unknown tool: {tool_name}")
    logger.info(
        "Calling tool",
        extra={
            "tool_name": tool_name,
            "arg_keys": list(tool_args.keys()),
            "tool_args": tool_args,
        },
    )
    return await tool_fn(**tool_args, conn=conn)


# -----------------------------------------------------------------------------
# Tool Definitions
# -----------------------------------------------------------------------------


@tool(args_schema=ListLifeAreasArgs)
async def list_life_areas(
    user_id: str, conn: aiosqlite.Connection | None = None
) -> list[db.LifeArea]:
    """List all life areas for a user."""
    return await LifeAreaMethods.list(user_id, conn=conn)


@tool(args_schema=GetLifeAreaArgs)
async def get_life_area(
    user_id: str, area_id: str, conn: aiosqlite.Connection | None = None
) -> db.LifeArea:
    """Fetch a single life area by id for a user."""
    return await LifeAreaMethods.get(user_id, area_id, conn=conn)


@tool(args_schema=CreateLifeAreaArgs)
async def create_life_area(
    user_id: str,
    title: str,
    parent_id: str | None = None,
    conn: aiosqlite.Connection | None = None,
) -> db.LifeArea:
    """Create a new life area for a user."""
    return await LifeAreaMethods.create(user_id, title, parent_id, conn=conn)


@tool(args_schema=DeleteLifeAreaArgs)
async def delete_life_area(
    user_id: str, area_id: str, conn: aiosqlite.Connection | None = None
) -> None:
    """Delete a life area by id for a user."""
    await LifeAreaMethods.delete(user_id, area_id, conn=conn)


@tool(args_schema=ListCriteriaArgs)
async def list_criteria(
    user_id: str, area_id: str, conn: aiosqlite.Connection | None = None
) -> list[db.Criteria]:
    """List criteria belonging to a life area."""
    return await CriteriaMethods.list(user_id, area_id, conn=conn)


@tool(args_schema=DeleteCriteriaArgs)
async def delete_criteria(
    user_id: str, criteria_id: str, conn: aiosqlite.Connection | None = None
) -> None:
    """Delete a criteria item by id for a user."""
    await CriteriaMethods.delete(user_id, criteria_id, conn=conn)


@tool(args_schema=CreateCriteriaArgs)
async def create_criteria(
    user_id: str,
    area_id: str,
    title: str,
    conn: aiosqlite.Connection | None = None,
) -> db.Criteria:
    """Create a criteria item under a life area."""
    return await CriteriaMethods.create(user_id, area_id, title, conn=conn)


@tool(args_schema=SetCurrentAreaArgs)
async def set_current_area(
    user_id: str, area_id: str, conn: aiosqlite.Connection | None = None
) -> db.LifeArea:
    """Set a life area as the current area for interview. Call this after creating an area when the user wants to be interviewed about it."""
    return await CurrentAreaMethods.set_current(user_id, area_id, conn=conn)


AREA_TOOLS = [
    create_life_area,
    delete_life_area,
    get_life_area,
    list_life_areas,
    create_criteria,
    delete_criteria,
    list_criteria,
    set_current_area,
]

# Auto-generate from AREA_TOOLS to avoid manual sync
# Note: async tools use .coroutine, sync tools use .func
TOOL_METHODS = {tool.name: tool.coroutine or tool.func for tool in AREA_TOOLS}
