import os
from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph, END
from langgraph.graph.message import add_messages

from .methods import AREA_TOOLS

MAX_LOOP_STEPS = 3


def get_api_key() -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key is None:
        raise ValueError("OPENROUTER_API_KEY is required")
    return api_key


model = ChatOpenAI(
    model="google/gemini-2.0-flash-001",
    api_key=get_api_key,
    base_url="https://openrouter.ai/api/v1",
)
model_with_tools = model.bind_tools(AREA_TOOLS)


class State(TypedDict):
    loop_step: int
    messages: Annotated[list[BaseMessage], add_messages]


def llm_node(state: State):
    return {"messages": model_with_tools.invoke(state["messages"])}


def tool_node(state: State):
    last_message = state["messages"][-1]
    tools_messages = build_tool_messages(last_message)
    return {"messages": tools_messages, "loop_step": state["loop_step"] + 1}


def router(state: State):
    if state["loop_step"] > MAX_LOOP_STEPS:
        return "threashold_node"
    if get_tool_calls(state["messages"][-1]):
        return "tools"
    return END


def threashold_node(*args, **kwargs):
    content = "Can you say this differently? (answer generation error)"
    ai_msg = AIMessage(content=content)
    return {"messages": [ai_msg]}


def build_tool_messages(last_message: BaseMessage):
    tools_messages = []
    for tool_call in get_tool_calls(last_message):
        tool_result = run_tool_call(tool_call)
        tools_messages.append(
            ToolMessage(
                content=str(tool_result),
                tool_call_id=tool_call["id"],
                name=tool_call["name"],
            )
        )
    return tools_messages


def run_tool_call(tool_call):
    name = tool_call["name"]
    args = tool_call["args"]
    for tool in AREA_TOOLS:
        if tool.name == name:
            return tool.invoke(args)
    raise ValueError(f"Unknown tool: {name}")


def get_tool_calls(message: BaseMessage):
    return getattr(message, "tool_calls", [])


def get_subgraph():
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", llm_node)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_node("threashold_node", threashold_node)

    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges("chatbot", router)
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge("threashold_node", END)

    return graph_builder.compile()
