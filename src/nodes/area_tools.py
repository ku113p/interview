from typing_extensions import TypedDict

from typing_extensions import TypedDict

from langchain_core.messages import AIMessage, ToolMessage

from src.routers.area_router import call_tool


class State(TypedDict):
    loop_step: int
    messages: list


def area_tools(state: State):
    last_message: AIMessage = state["messages"][-1]

    tools_messages = []
    for tool_call in last_message.tool_calls:
        tool_result = call_tool(tool_call)  # type: ignore[arg-type]
        t_msg = ToolMessage(
            content=str(tool_result),
            tool_call_id=tool_call["id"],
            name=tool_call["name"],
        )
        tools_messages.append(t_msg)

    return {"messages": tools_messages, "loop_step": state["loop_step"] + 1}
