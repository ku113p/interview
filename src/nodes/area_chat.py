import os
from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages

from src.routers.area_router import AREA_TOOLS


model = ChatOpenAI(
    model="google/gemini-2.0-flash-001",
    base_url="https://openrouter.ai/api/v1",
)
model_with_tools = model.bind_tools(AREA_TOOLS)


class State(TypedDict):
    loop_step: int
    messages: Annotated[list[BaseMessage], add_messages]


def area_chat(state: State):
    return {"messages": model_with_tools.invoke(state["messages"])}
