from typing import Annotated

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from src.domain.models import User
from src.shared.message_buckets import MessageBuckets, merge_message_buckets
from src.shared.timestamp import get_timestamp


class State(BaseModel):
    user: User
    text: str
    messages: Annotated[list[BaseMessage], add_messages]
    messages_to_save: Annotated[MessageBuckets, merge_message_buckets]


async def build_user_message(state: State):
    new_msg = HumanMessage(content=state.text)

    return {"messages": [new_msg], "messages_to_save": {get_timestamp(): [new_msg]}}
