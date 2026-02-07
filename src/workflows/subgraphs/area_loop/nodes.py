"""Area loop graph nodes."""

import logging
import sqlite3
from typing import cast

from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.messages.tool import ToolCall

from src.infrastructure.db import transaction
from src.shared.message_buckets import MessageBuckets
from src.shared.timestamp import get_timestamp
from src.workflows.subgraphs.area_loop.state import AreaState
from src.workflows.subgraphs.area_loop.tools import AREA_TOOLS, call_tool

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# area_chat node
# -----------------------------------------------------------------------------


async def area_chat(state: AreaState, llm):
    """Process user input and generate response with tool calls."""
    logger.info("Running area chat", extra={"message_count": len(state.messages)})
    model = llm.bind_tools(AREA_TOOLS)
    system_message = SystemMessage(
        f"You are a helpful assistant for managing life areas (also called topics) and their criteria. "
        f"You have access to tools to create, view, modify, and delete life areas and their criteria. "
        f"User ID: {state.user.id}\n\n"
        f"Use the available tools for area CRUD operations when the user wants to:\n"
        f"- Create, edit, delete, or view life areas\n"
        f"- Create, edit, delete, or list criteria for a life area\n"
        f"- Switch to or discuss a specific life area\n"
        f"- Set a life area as current for interview\n\n"
        f"IMPORTANT: When working with criteria:\n"
        f"- Area IDs are UUIDs (e.g., '06985990-c0d4-7293-8000-...')\n"
        f"- If you don't know the area_id, call 'list_life_areas' first\n"
        f"- Extract the 'id' field from responses, never use the title as area_id\n\n"
        f"IMPORTANT: After creating a life area, ALWAYS ask the user:\n"
        f"'Would you like to set this area as the current area for interview?'\n"
        f"If they say yes, use 'set_current_area' tool with the area_id.\n"
        f"This ensures the interview will use this area and its criteria.\n\n"
        f"You should also help users by:\n"
        f"- Suggesting relevant criteria for their topics when asked\n"
        f"- Providing examples and recommendations\n"
        f"- Answering questions about life areas and criteria\n"
        f"- Being conversational and helpful, not just executing tools\n\n"
        f"Choose the appropriate tools based on the user's intent, "
        f"but also engage in helpful conversation when the user needs guidance or suggestions."
    )
    message = await model.ainvoke([system_message, *state.messages])
    return {"messages": [message], "messages_to_save": {get_timestamp(): [message]}}


# -----------------------------------------------------------------------------
# area_tools node
# -----------------------------------------------------------------------------


class ToolExecutionError(Exception):
    """Error during tool execution with associated ToolMessage."""

    def __init__(self, message: ToolMessage) -> None:
        super().__init__("Tool execution failed")
        self.message = message


def _build_tool_message(tool_call: dict[str, object], content: str) -> ToolMessage:
    return ToolMessage(
        content=content,
        tool_call_id=tool_call["id"],
        name=tool_call["name"],
    )


def _record_message(messages_to_save: MessageBuckets, message: ToolMessage) -> None:
    ts = get_timestamp()
    if ts in messages_to_save:
        messages_to_save[ts].append(message)
    else:
        messages_to_save[ts] = [message]


def _fallback_tool_failure() -> ToolMessage:
    return ToolMessage(
        content="tool_error: ToolFailure",
        tool_call_id="unknown",
        name="unknown",
    )


def _validate_tool_call(call: dict[str, object]) -> str | None:
    """Validate tool call structure. Returns error message or None if valid."""
    if not isinstance(call, dict):
        return "tool_call must be a dictionary"
    if "id" not in call or not isinstance(call.get("id"), str):
        return "tool_call missing required 'id' field"
    if "name" not in call or not isinstance(call.get("name"), str):
        return "tool_call missing required 'name' field"
    return None


async def _execute_tool_call(call: ToolCall, conn: sqlite3.Connection) -> ToolMessage:
    call_dict = cast(dict[str, object], call)
    validation_error = _validate_tool_call(call_dict)
    if validation_error:
        raise ToolExecutionError(
            _build_tool_message(
                {
                    "id": call_dict.get("id", "unknown"),
                    "name": call_dict.get("name", "unknown"),
                },
                f"tool_error: ValidationError: {validation_error}",
            )
        )
    try:
        tool_result = await call_tool(call, conn=conn)
    except Exception as exc:
        raise ToolExecutionError(
            _build_tool_message(
                call_dict,
                f"tool_error: {type(exc).__name__}: {exc}",
            )
        ) from exc
    return _build_tool_message(
        call_dict,
        str(tool_result),
    )


async def _execute_all_tools(
    tool_calls: list[dict[str, object]], conn: sqlite3.Connection
) -> tuple[list[ToolMessage], MessageBuckets]:
    """Execute all tool calls and collect results."""
    tools_messages: list[ToolMessage] = []
    messages_to_save: MessageBuckets = {}
    for tool_call in tool_calls:
        call = cast(ToolCall, tool_call)
        t_msg = await _execute_tool_call(call, conn)
        tools_messages.append(t_msg)
        _record_message(messages_to_save, t_msg)
    return tools_messages, messages_to_save


def _make_failure_result(
    msg: ToolMessage,
) -> tuple[list[ToolMessage], MessageBuckets, bool]:
    """Create a failure result tuple."""
    return [msg], {get_timestamp(): [msg]}, False


async def _run_tool_calls(
    tool_calls: list[dict[str, object]],
) -> tuple[list[ToolMessage], MessageBuckets, bool]:
    logger.info("Executing tool calls", extra={"count": len(tool_calls)})
    try:
        with transaction() as conn:
            conn = cast(sqlite3.Connection, conn)
            messages, to_save = await _execute_all_tools(tool_calls, conn)
        return messages, to_save, True
    except ToolExecutionError as exc:
        logger.warning("Tool execution error")
        return _make_failure_result(exc.message)
    except Exception:
        logger.exception("Unexpected tool execution failure")
        return _make_failure_result(_fallback_tool_failure())


async def area_tools(state: AreaState):
    """Execute tool calls from the last message."""
    last_message = state.messages[-1]
    success = state.success if state.success is not None else True
    tool_calls = cast(
        list[dict[str, object]], getattr(last_message, "tool_calls", None) or []
    )
    tools_messages: list[ToolMessage] = []
    messages_to_save: MessageBuckets = {}
    if tool_calls:
        logger.info("Handling tool calls", extra={"count": len(tool_calls)})
        tools_messages, messages_to_save, call_success = await _run_tool_calls(
            tool_calls
        )
        if not call_success:
            success = False

    logger.info("Tool handling completed", extra={"success": success})
    return {
        "messages": tools_messages,
        "messages_to_save": messages_to_save,
        "success": success,
    }


# -----------------------------------------------------------------------------
# area_end node
# -----------------------------------------------------------------------------


def area_end(state: AreaState):
    """Finalize the area loop, setting success if not already set."""
    if state.success is None:
        return {"success": True}
    return {}
