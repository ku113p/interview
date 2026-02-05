from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from src.shared.message_buckets import MessageBuckets, merge_message_buckets


class State(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]
    messages_to_save: Annotated[MessageBuckets, merge_message_buckets]
    success: bool | None = None


def area_end(state: State):
    if state.success is None:
        return {"success": True}
    return {}
