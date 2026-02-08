"""Area loop graph nodes."""

import logging
import sqlite3
from typing import cast

from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.messages.tool import ToolCall

from src.infrastructure.db import transaction
from src.shared.message_buckets import MessageBuckets
from src.shared.prompts import build_area_chat_prompt
from src.shared.retry import invoke_with_retry
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
    prompt_content = build_area_chat_prompt(user_id=str(state.user.id))
    system_message = SystemMessage(prompt_content)
    messages = [system_message, *state.messages]
    message = await invoke_with_retry(lambda: model.ainvoke(messages))
    return {"messages": [message], "messages_to_save": {get_timestamp(): [message]}}


# -----------------------------------------------------------------------------
# area_tools node
# -----------------------------------------------------------------------------


class ToolExecutionError(Exception):
    """Error during tool execution with associated ToolMessage."""

    def __init__(self, message: ToolMessage) -> None:
        super().__init__("Tool execution failed")
        self.message = message


def _validate_tool_call(call_dict: dict[str, object]) -> tuple[str, str]:
    """Validate tool call structure and return (call_id, call_name)."""
    if not isinstance(call_dict, dict):
        raise ToolExecutionError(
            ToolMessage(
                content="tool_error: ValidationError: tool_call must be a dictionary",
                tool_call_id="unknown",
                name="unknown",
            )
        )
    call_id = call_dict.get("id", "unknown")
    call_name = call_dict.get("name", "unknown")
    if not isinstance(call_id, str) or not isinstance(call_name, str):
        raise ToolExecutionError(
            ToolMessage(
                content="tool_error: ValidationError: tool_call missing required fields",
                tool_call_id=str(call_id),
                name=str(call_name),
            )
        )
    return call_id, call_name


async def _execute_tool_call(
    call: dict[str, object], conn: sqlite3.Connection
) -> ToolMessage:
    """Execute a single tool call and return the result message."""
    call_id, call_name = _validate_tool_call(call)
    try:
        result = await call_tool(cast(ToolCall, call), conn=conn)
    except Exception as exc:
        raise ToolExecutionError(
            ToolMessage(
                content=f"tool_error: {type(exc).__name__}: {exc}",
                tool_call_id=call_id,
                name=call_name,
            )
        ) from exc
    return ToolMessage(content=str(result), tool_call_id=call_id, name=call_name)


def _make_result(
    messages: list[ToolMessage], messages_to_save: MessageBuckets, success: bool
) -> dict[str, list[ToolMessage] | MessageBuckets | bool]:
    """Create a result dict for area_tools."""
    return {
        "messages": messages,
        "messages_to_save": messages_to_save,
        "success": success,
    }


async def _run_tool_calls(
    tool_calls: list[dict[str, object]],
) -> tuple[list[ToolMessage], MessageBuckets]:
    """Execute all tool calls within a transaction."""
    messages: list[ToolMessage] = []
    messages_to_save: MessageBuckets = {}
    with transaction() as conn:
        conn = cast(sqlite3.Connection, conn)
        for call in tool_calls:
            msg = await _execute_tool_call(call, conn)
            messages.append(msg)
            messages_to_save.setdefault(get_timestamp(), []).append(msg)
    return messages, messages_to_save


async def area_tools(state: AreaState):
    """Execute tool calls from the last message."""
    tool_calls = cast(
        list[dict[str, object]],
        getattr(state.messages[-1], "tool_calls", None) or [],
    )
    if not tool_calls:
        return _make_result([], {}, state.success)

    logger.info("Executing tool calls", extra={"count": len(tool_calls)})
    try:
        messages, messages_to_save = await _run_tool_calls(tool_calls)
    except ToolExecutionError as exc:
        logger.warning("Tool execution error")
        return _make_result([exc.message], {get_timestamp(): [exc.message]}, False)
    except Exception:
        logger.exception("Unexpected tool execution failure")
        fallback = ToolMessage(
            content="tool_error: ToolFailure", tool_call_id="unknown", name="unknown"
        )
        return _make_result([fallback], {get_timestamp(): [fallback]}, False)

    success = state.success if state.success is not None else True
    logger.info("Tool handling completed", extra={"success": success})
    return _make_result(messages, messages_to_save, success)


# -----------------------------------------------------------------------------
# area_end node
# -----------------------------------------------------------------------------


def area_end(state: AreaState):
    """Finalize the area loop, setting success if not already set."""
    if state.success is None:
        return {"success": True}
    return {}
