import logging
from typing import Annotated

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel

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


def get_formatted_history(user_obj: User, limit: int = 10) -> list[BaseMessage]:
    msgs = sorted(
        db.HistoryManager.list_by_user(user_obj.id), key=lambda x: x.created_ts
    )
    domain_msgs = [msg.data for msg in msgs[-limit:]]

    formatted_messages = []
    for msg in domain_msgs:
        if msg["role"] == "user":
            formatted_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "ai":
            formatted_messages.append(
                AIMessage(content=msg["content"], tool_calls=msg.get("tool_calls"))
            )
        elif msg["role"] == "tool":
            formatted_messages.append(
                ToolMessage(
                    content=msg["content"],
                    tool_call_id=msg.get("tool_call_id", "history"),
                    name=msg.get("name", "history"),
                )
            )
        else:
            raise NotImplementedError()

    return formatted_messages
