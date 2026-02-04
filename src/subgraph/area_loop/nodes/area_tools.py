from typing import Annotated, cast

from langchain_core.messages import BaseMessage, ToolMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from src.subgraph.area_loop.tools import call_tool


class State(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]
    messages_to_save: Annotated[list[BaseMessage], add_messages]
    success: bool | None = None


async def area_tools(state: State):
    last_message = state.messages[-1]

    tools_messages = []
    success = state.success if state.success is not None else True
    tool_calls = cast(list, getattr(last_message, "tool_calls", None) or [])
    for tool_call in tool_calls:
        try:
            tool_result = await call_tool(tool_call)
            content = str(tool_result)
        except Exception as exc:
            content = f"tool_error: {type(exc).__name__}: {exc}"
            success = False

        t_msg = ToolMessage(
            content=content,
            tool_call_id=tool_call["id"],
            name=tool_call["name"],
        )
        tools_messages.append(t_msg)

    return {
        "messages": tools_messages,
        "messages_to_save": tools_messages,
        "success": success,
    }
