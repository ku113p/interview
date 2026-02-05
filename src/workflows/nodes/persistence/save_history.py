import logging
from typing import Annotated

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from pydantic import BaseModel

from src.domain.models import User
from src.infrastructure.db import repositories as db
from src.shared.ids import new_id
from src.shared.message_buckets import MessageBuckets, merge_message_buckets
from src.shared.utils.content import normalize_content

logger = logging.getLogger(__name__)


class State(BaseModel):
    user: User
    messages_to_save: Annotated[MessageBuckets, merge_message_buckets]
    success: bool | None = None


def _normalize_role(role: str) -> str:
    if role == "human":
        return "user"
    if role == "ai":
        return "ai"
    if role == "tool":
        return "tool"
    return "ai"


def _message_to_dict(msg: BaseMessage) -> dict[str, object]:
    role = getattr(msg, "type", None) or msg.__class__.__name__.lower()
    content = normalize_content(msg.content)
    data: dict[str, object] = {"role": _normalize_role(str(role)), "content": content}
    if isinstance(msg, AIMessage):
        tool_calls = getattr(msg, "tool_calls", None)
        if tool_calls:
            data["tool_calls"] = tool_calls
    if isinstance(msg, ToolMessage):
        data["tool_call_id"] = str(msg.tool_call_id)
        if msg.name:
            data["name"] = msg.name
    return data


def save_history(state: State) -> dict:
    messages_by_ts = state.messages_to_save or {}
    if not messages_by_ts:
        logger.debug("No messages to save", extra={"user_id": str(state.user.id)})
        return {}

    message_count = sum(len(messages) for messages in messages_by_ts.values())
    logger.info(
        "Saving history",
        extra={"user_id": str(state.user.id), "count": message_count},
    )

    for created_ts, messages in messages_by_ts.items():
        for msg in messages:
            history_id = new_id()
            db.HistoryManager.create(
                history_id,
                db.History(
                    id=history_id,
                    data=_message_to_dict(msg),
                    user_id=state.user.id,
                    created_ts=created_ts,
                ),
            )

    return {}
