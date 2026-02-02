from typing import Annotated
from pydantic import BaseModel

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langgraph.graph.message import add_messages

from src.routers.area_router import call_tool


class State(BaseModel):
    loop_step: int
    messages: Annotated[list[BaseMessage], add_messages]


async def area_tools(state: State):
    last_message: AIMessage = state.messages[-1]

    tools_messages = []
    for tool_call in last_message.tool_calls:
        tool_result = await call_tool(tool_call)
        t_msg = ToolMessage(
            content=str(tool_result),
            tool_call_id=tool_call["id"],
            name=tool_call["name"],
        )
        tools_messages.append(t_msg)

    return {"messages": tools_messages, "loop_step": state.loop_step + 1}
