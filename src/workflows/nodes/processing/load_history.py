import logging
import uuid
from typing import Annotated, Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from src.config.settings import HISTORY_LIMIT_GLOBAL
from src.domain.models import User
from src.infrastructure.db import managers as db

logger = logging.getLogger(__name__)


class LoadHistoryState(BaseModel):
    user: User
    messages: Annotated[list[BaseMessage], add_messages]


async def load_history(state: LoadHistoryState):
    history_messages = get_formatted_history(state.user)
    logger.info(
        "Loaded history",
        extra={"user_id": str(state.user.id), "count": len(history_messages)},
    )
    return {"messages": history_messages}


def _validate_tool_calls(tool_calls: list, user_id: uuid.UUID) -> list[dict]:
    """Filter and validate tool_calls, returning only valid ones."""
    valid = []
    for tool_call in tool_calls:
        if isinstance(tool_call, dict) and "id" in tool_call and "name" in tool_call:
            valid.append(tool_call)
        else:
            logger.warning(
                "Skipping malformed tool_call", extra={"user_id": str(user_id)}
            )
    return valid


def _convert_ai_message(message_dict: dict[str, Any], user_id: uuid.UUID) -> AIMessage:
    """Convert a raw AI message dict to AIMessage."""
    tool_calls = _validate_tool_calls(message_dict.get("tool_calls") or [], user_id)
    return AIMessage(content=message_dict["content"], tool_calls=tool_calls)


def _convert_tool_message(message_dict: dict[str, Any]) -> ToolMessage:
    """Convert a raw tool message dict to ToolMessage."""
    return ToolMessage(
        content=message_dict["content"],
        tool_call_id=message_dict.get("tool_call_id", "history"),
        name=message_dict.get("name", "history"),
    )


def get_formatted_history(
    user_obj: User, limit: int = HISTORY_LIMIT_GLOBAL
) -> list[BaseMessage]:
    history_entries = sorted(
        db.HistoriesManager.list_by_user(user_obj.id), key=lambda x: x.created_ts
    )
    message_dicts = [entry.data for entry in history_entries[-limit:]]

    formatted_messages = []
    for message_dict in message_dicts:
        role = message_dict.get("role")
        if role == "user":
            formatted_messages.append(HumanMessage(content=message_dict["content"]))
        elif role == "ai":
            formatted_messages.append(_convert_ai_message(message_dict, user_obj.id))
        elif role == "tool":
            formatted_messages.append(_convert_tool_message(message_dict))
        else:
            logger.warning("Skipping unknown role", extra={"role": role})

    return formatted_messages
