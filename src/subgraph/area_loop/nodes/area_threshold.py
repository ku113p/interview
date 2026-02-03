from typing import Annotated

from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel


class State(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]


async def area_threshold():
    content = "Can you say this differently? (answer generation error)"
    ai_msg = AIMessage(content=content)
    return {"messages": [ai_msg]}
