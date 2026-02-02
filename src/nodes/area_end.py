from typing import Annotated
from pydantic import BaseModel

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class State(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]


def area_end(state: State):
    return state
