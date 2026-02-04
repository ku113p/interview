from functools import partial

from langgraph.graph import END, START, StateGraph

from src.ai import NewAI
from src.nodes.build_user_message import build_user_message
from src.nodes.extract_target import extract_target
from src.nodes.interview import interview
from src.nodes.load_history import load_history
from src.nodes.save_history import save_history
from src.routers.history_router import route_history_save
from src.routers.message_router import route_message
from src.state import State
from src.subgraph.area_loop.flow import MAX_AREA_RECURSION
from src.subgraph.area_loop.graph import build_area_graph
from src.subgraph.extract_flow.graph import build_extract_graph

MODEL_NAME_FLASH = "google/gemini-2.0-flash-001"


def _add_nodes(builder: StateGraph, extract_graph, area_graph) -> None:
    builder.add_node("extract_text", extract_graph)
    builder.add_node("load_history", load_history)
    builder.add_node("build_user_message", build_user_message)
    builder.add_node(
        "extract_target",
        partial(extract_target, llm=NewAI(MODEL_NAME_FLASH, 0).build()),
    )
    builder.add_node(
        "interview", partial(interview, llm=NewAI(MODEL_NAME_FLASH).build())
    )
    builder.add_node("save_history", save_history)
    builder.add_node("area_loop", area_graph)


def _add_edges(builder: StateGraph) -> None:
    builder.add_edge(START, "extract_text")
    builder.add_edge("extract_text", "load_history")
    builder.add_edge("load_history", "build_user_message")
    builder.add_edge("build_user_message", "extract_target")
    builder.add_conditional_edges("extract_target", route_message)
    builder.add_conditional_edges(
        "interview", route_history_save, ["save_history", END]
    )
    builder.add_conditional_edges(
        "area_loop", route_history_save, ["save_history", END]
    )
    builder.add_edge("save_history", END)


def get_graph():
    builder = StateGraph(State)
    extract_graph = build_extract_graph(NewAI(MODEL_NAME_FLASH, 0).build())
    area_graph = build_area_graph(NewAI(MODEL_NAME_FLASH).build()).with_config(
        {"recursion_limit": MAX_AREA_RECURSION}
    )
    _add_nodes(builder, extract_graph, area_graph)
    _add_edges(builder)
    return builder.compile()
