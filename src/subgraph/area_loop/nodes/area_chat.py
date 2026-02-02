from typing import Annotated
from pydantic import BaseModel

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from src.subgraph.area_loop.tools import AREA_TOOLS


class State(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]


async def area_chat(state: State, llm):
    model = llm.bind_tools(AREA_TOOLS)
    message = await model.ainvoke(state.messages)
    return {"messages": [message]}
