from typing import Annotated
from pydantic import BaseModel

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages

from src.routers.area_router import AREA_TOOLS


class State(BaseModel):
    loop_step: int
    messages: Annotated[list[BaseMessage], add_messages]


async def area_chat(state: State, llm: ChatOpenAI):
    llm = llm.bind_tools(AREA_TOOLS)
    message = await llm.ainvoke(state.messages)
    return {"messages": [message]}
