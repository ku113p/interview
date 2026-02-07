import logging
import uuid
from typing import Annotated, Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from src.config.settings import HISTORY_LIMIT_GLOBAL
from src.domain.models import User
from src.infrastructure.db import repositories as db

logger = logging.getLogger(__name__)


class State(BaseModel):
    user: User
    messages: Annotated[list[BaseMessage], add_messages]


async def load_history(state: State):
    msgs = get_formatted_history(state.user)
    logger.info(
        "Loaded history",
        extra={"user_id": str(state.user.id), "count": len(msgs)},
    )
    return {"messages": msgs}


def _validate_tool_calls(tool_calls: list, user_id: uuid.UUID) -> list[dict]:
    """Filter and validate tool_calls, returning only valid ones."""
    valid = []
    for tc in tool_calls:
        if isinstance(tc, dict) and "id" in tc and "name" in tc:
            valid.append(tc)
        else:
            logger.warning(
                "Skipping malformed tool_call", extra={"user_id": str(user_id)}
            )
    return valid


def _convert_ai_message(msg: dict[str, Any], user_id: uuid.UUID) -> AIMessage:
    """Convert a raw AI message dict to AIMessage."""
    tool_calls = _validate_tool_calls(msg.get("tool_calls") or [], user_id)
    return AIMessage(content=msg["content"], tool_calls=tool_calls)


def _convert_tool_message(msg: dict[str, Any]) -> ToolMessage:
    """Convert a raw tool message dict to ToolMessage."""
    return ToolMessage(
        content=msg["content"],
        tool_call_id=msg.get("tool_call_id", "history"),
        name=msg.get("name", "history"),
    )


def get_formatted_history(
    user_obj: User, limit: int = HISTORY_LIMIT_GLOBAL
) -> list[BaseMessage]:
    msgs = sorted(
        db.HistoryManager.list_by_user(user_obj.id), key=lambda x: x.created_ts
    )
    domain_msgs = [msg.data for msg in msgs[-limit:]]

    formatted_messages = []
    for msg in domain_msgs:
        role = msg.get("role")
        if role == "user":
            formatted_messages.append(HumanMessage(content=msg["content"]))
        elif role == "ai":
            formatted_messages.append(_convert_ai_message(msg, user_obj.id))
        elif role == "tool":
            formatted_messages.append(_convert_tool_message(msg))
        else:
            logger.warning("Skipping unknown role", extra={"role": role})

    return formatted_messages
