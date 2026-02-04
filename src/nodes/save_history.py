import uuid
from typing import Annotated

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from src import db
from src.domain import user


class State(BaseModel):
    user: user.User
    messages_to_save: Annotated[list[BaseMessage], add_messages]
    success: bool | None = None


def _normalize_role(role: str) -> str:
    if role == "human":
        return "user"
    if role == "ai":
        return "ai"
    if role == "tool":
        return "tool"
    return "ai"


def _normalize_content(content: object) -> str:
    if isinstance(content, list):
        return "".join(str(part) for part in content)
    if isinstance(content, str):
        return content
    return str(content)


def _message_to_dict(msg: BaseMessage) -> dict[str, object]:
    role = getattr(msg, "type", None) or msg.__class__.__name__.lower()
    content = _normalize_content(msg.content)
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
    messages = state.messages_to_save or []
    if not messages:
        return {}

    for msg in messages:
        history_id = uuid.uuid4()
        db.HistoryManager.create(
            history_id,
            db.History(
                id=history_id,
                data=_message_to_dict(msg),
                user_id=state.user.id,
                created_ts=0,
            ),
        )

    return {}
