from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langgraph.graph import START, StateGraph, END
from langgraph.graph.message import add_messages

from src.graphs.deps import Deps

MAX_LOOP_STEPS = 3


class State(TypedDict):
    loop_step: int
    messages: Annotated[list[BaseMessage], add_messages]


def build_llm_node(deps: Deps):
    tools_llm = deps["build_llm"](temperature=0).bind_tools(deps["get_area_tools"]())

    async def llm_node(state: State):
        loop_state = state["loop_step"]
        tools_messages = await tools_llm.ainvoke(state["messages"])
        return {"messages": tools_messages, "loop_step": loop_state}

    return llm_node


def build_tool_node(deps: Deps):
    async def tool_node(state: State):
        last_message = state["messages"][-1]
        tools_messages = await build_tool_messages(last_message, deps)
        loop_step = state["loop_step"] + 1
        return {"messages": tools_messages, "loop_step": loop_step}

    return tool_node


def router(state: State):
    loop_step = state["loop_step"]
    if loop_step > MAX_LOOP_STEPS:
        return "threashold_node"
    if get_tool_calls(state["messages"][-1]):
        return "tools"
    return END


def threashold_node(*args, **kwargs):
    content = "Can you say this differently? (answer generation error)"
    ai_msg = AIMessage(content=content)
    return {"messages": [ai_msg]}


async def build_tool_messages(last_message: BaseMessage, deps: Deps):
    tools_messages = []
    for tool_call in get_tool_calls(last_message):
        tool_result = await run_tool_call(tool_call, deps)
        tools_messages.append(
            ToolMessage(
                content=str(tool_result),
                tool_call_id=tool_call["id"],
                name=tool_call["name"],
            )
        )
    return tools_messages


async def run_tool_call(tool_call, deps: Deps):
    name = tool_call["name"]
    args = tool_call["args"]
    for tool in deps["get_area_tools"]():
        if tool.name == name:
            return await tool.ainvoke(args)
    raise ValueError(f"Unknown tool: {name}")


def get_tool_calls(message: BaseMessage):
    return getattr(message, "tool_calls", [])


def get_subgraph(deps: Deps):
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", build_llm_node(deps))
    graph_builder.add_node("tools", build_tool_node(deps))
    graph_builder.add_node("threashold_node", threashold_node)

    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges("chatbot", router)
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge("threashold_node", END)

    return graph_builder.compile()
