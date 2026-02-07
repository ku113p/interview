"""Area loop subgraph definition."""

from functools import partial
from typing import Literal

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from src.workflows.subgraphs.area_loop.nodes import area_chat, area_end, area_tools
from src.workflows.subgraphs.area_loop.state import AreaState

# Max tool iterations per area loop (prevents infinite loops)
MAX_LOOP_STEPS = 10
# Max recursion depth: 2 * (MAX_LOOP_STEPS + 1) + 1
# Accounts for tool call/response cycle + routing overhead
MAX_AREA_RECURSION = 2 * (MAX_LOOP_STEPS + 1) + 1


def route_area(state: AreaState) -> Literal["area_tools", "area_end"]:
    """Route based on whether the last message has tool calls."""
    if not state.messages:
        return "area_end"
    tool_calls = getattr(state.messages[-1], "tool_calls", None)
    if tool_calls and len(tool_calls) > 0:
        return "area_tools"
    return "area_end"


def build_area_graph(llm: ChatOpenAI):
    """Build and compile the area loop subgraph."""
    area_builder = StateGraph(AreaState)
    area_builder.add_node("area_chat", partial(area_chat, llm=llm))
    area_builder.add_node("area_tools", area_tools)
    area_builder.add_node("area_end", area_end)
    area_builder.add_edge(START, "area_chat")
    area_builder.add_conditional_edges(
        "area_chat", route_area, ["area_tools", "area_end"]
    )
    area_builder.add_edge("area_tools", "area_chat")
    area_builder.add_edge("area_end", END)
    return area_builder.compile()
