"""Area loop tools, schemas, and tool registry."""

import logging
import uuid
from typing import Annotated

import aiosqlite
from langchain.tools import tool
from langchain_core.messages.tool import ToolCall
from pydantic import AfterValidator, BaseModel, Field

from src.infrastructure.db import managers as db

from .methods import CurrentAreaMethods, LifeAreaMethods

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# UUID Validation
# -----------------------------------------------------------------------------


def _validate_uuid(value: str) -> str:
    """Validate and normalize a string to canonical UUID format."""
    try:
        parsed = uuid.UUID(value)
    except ValueError as exc:
        logger.warning("Invalid UUID input", extra={"value": value})
        raise ValueError(f"Invalid UUID: {value}") from exc
    normalized = str(parsed)
    if normalized != value:
        logger.debug(
            "UUID normalized",
            extra={"input": value, "output": normalized},
        )
    return normalized


UUIDStr = Annotated[str, AfterValidator(_validate_uuid)]


# -----------------------------------------------------------------------------
# Argument Schemas
# -----------------------------------------------------------------------------


class ListLifeAreasArgs(BaseModel):
    """Arguments for listing life areas."""


class GetLifeAreaArgs(BaseModel):
    """Arguments for getting a single life area."""

    area_id: UUIDStr = Field(..., description="UUID of the life area to fetch")


class CreateLifeAreaArgs(BaseModel):
    """Arguments for creating a life area."""

    title: str = Field(..., description="Title/name for the new life area")
    parent_id: UUIDStr | None = Field(
        None,
        description="Optional UUID of parent life area for hierarchical organization",
    )


class DeleteLifeAreaArgs(BaseModel):
    """Arguments for deleting a life area."""

    area_id: UUIDStr = Field(..., description="UUID of the life area to delete")


class SetCurrentAreaArgs(BaseModel):
    """Arguments for setting the current area for interview."""

    area_id: UUIDStr = Field(
        ...,
        description="UUID of the life area to set as current for interview",
    )


class SubAreaNode(BaseModel):
    """A node in the subtree with optional children."""

    title: str = Field(..., description="Title/name for this sub-area")
    children: list["SubAreaNode"] = Field(
        default_factory=list,
        description="Nested children sub-areas",
    )


class CreateSubtreeArgs(BaseModel):
    """Arguments for creating a subtree of life areas."""

    parent_id: UUIDStr = Field(
        ..., description="UUID of parent life area to attach subtree to"
    )
    subtree: list[SubAreaNode] = Field(
        ..., description="List of top-level nodes with nested children"
    )


# -----------------------------------------------------------------------------
# Tool Calling
# -----------------------------------------------------------------------------


async def call_tool(
    tool_call: ToolCall, user_id: str, conn: aiosqlite.Connection | None = None
):
    """Execute a tool call by name with given arguments."""
    tool_name = tool_call["name"]
    tool_args = dict(tool_call.get("args", {}) or {})
    tool_args.pop("conn", None)
    tool_args["user_id"] = user_id

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


@tool(args_schema=SetCurrentAreaArgs)
async def set_current_area(
    user_id: str, area_id: str, conn: aiosqlite.Connection | None = None
) -> db.LifeArea:
    """Set a life area as the current area for interview. Call this after creating an area when the user wants to be interviewed about it."""
    return await CurrentAreaMethods.set_current(user_id, area_id, conn=conn)


@tool(args_schema=CreateSubtreeArgs)
async def create_subtree(
    user_id: str,
    parent_id: str,
    subtree: list[SubAreaNode],
    conn: aiosqlite.Connection | None = None,
) -> str:
    """Create multiple nested sub-areas at once under a parent area.

    Use this tool when creating a hierarchy of sub-areas (e.g., job positions
    with their responsibilities, achievements, projects). More efficient than
    multiple create_life_area calls.

    Example subtree structure:
    [
        {"title": "Google - Engineer", "children": [
            {"title": "Responsibilities"},
            {"title": "Achievements"}
        ]},
        {"title": "Amazon - SDE", "children": [
            {"title": "Projects"}
        ]}
    ]
    """
    created = await LifeAreaMethods.create_subtree(
        user_id, parent_id, subtree, conn=conn
    )
    # Return summary for LLM context
    titles = [area.title for area in created]
    return f"Created {len(created)} sub-areas: {', '.join(titles)}"


AREA_TOOLS = [
    create_life_area,
    create_subtree,
    delete_life_area,
    get_life_area,
    list_life_areas,
    set_current_area,
]

# Auto-generate from AREA_TOOLS to avoid manual sync
# Note: async tools use .coroutine, sync tools use .func
TOOL_METHODS = {tool.name: tool.coroutine or tool.func for tool in AREA_TOOLS}
