import logging
import sqlite3
from typing import Annotated, cast

from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.messages.tool import ToolCall
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from src.infrastructure.db import transaction
from src.shared.message_buckets import MessageBuckets, merge_message_buckets
from src.shared.timestamp import get_timestamp
from src.workflows.subgraphs.area_loop.tools import call_tool

logger = logging.getLogger(__name__)


class State(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]
    messages_to_save: Annotated[MessageBuckets, merge_message_buckets]
    success: bool | None = None


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


class ToolExecutionError(Exception):
    def __init__(self, message: ToolMessage) -> None:
        super().__init__("Tool execution failed")
        self.message = message


async def _execute_tool_call(call: ToolCall, conn: sqlite3.Connection) -> ToolMessage:
    try:
        tool_result = await call_tool(call, conn=conn)
    except Exception as exc:
        raise ToolExecutionError(
            _build_tool_message(
                cast(dict[str, object], call),
                f"tool_error: {type(exc).__name__}: {exc}",
            )
        ) from exc
    return _build_tool_message(
        cast(dict[str, object], call),
        str(tool_result),
    )


async def _run_tool_calls(  # noqa: PLR0915
    tool_calls: list[dict[str, object]],
) -> tuple[list[ToolMessage], MessageBuckets, bool]:
    tools_messages: list[ToolMessage] = []
    messages_to_save: MessageBuckets = {}
    try:
        logger.info("Executing tool calls", extra={"count": len(tool_calls)})
        with transaction() as conn:
            conn = cast(sqlite3.Connection, conn)
            for tool_call in tool_calls:
                call = cast(ToolCall, tool_call)
                t_msg = await _execute_tool_call(call, conn)
                tools_messages.append(t_msg)
                _record_message(messages_to_save, t_msg)
    except ToolExecutionError as exc:
        logger.warning("Tool execution error")
        failed_message = exc.message
        return [failed_message], {get_timestamp(): [failed_message]}, False
    except Exception:
        logger.exception("Unexpected tool execution failure")
        fallback = _fallback_tool_failure()
        return [fallback], {get_timestamp(): [fallback]}, False
    return tools_messages, messages_to_save, True


async def area_tools(state: State):
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
