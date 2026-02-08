from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from src.domain.models import User
from src.shared.message_buckets import MessageBuckets, merge_message_buckets


class AreaState(BaseModel):
    user: User
    messages: Annotated[list[BaseMessage], add_messages]
    messages_to_save: Annotated[MessageBuckets, merge_message_buckets]
    is_successful: bool | None = None
