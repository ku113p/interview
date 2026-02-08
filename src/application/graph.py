from functools import partial

from langgraph.graph import END, START, StateGraph

from src.application.state import State
from src.infrastructure.llms import (
    get_llm_area_chat,
    get_llm_extract_target,
    get_llm_interview_analysis,
    get_llm_interview_response,
    get_llm_transcribe,
)
from src.workflows.nodes.input.build_user_message import build_user_message
from src.workflows.nodes.input.extract_target import extract_target
from src.workflows.nodes.persistence.save_history import save_history
from src.workflows.nodes.processing.interview_analysis import interview_analysis
from src.workflows.nodes.processing.interview_response import interview_response
from src.workflows.nodes.processing.load_history import load_history
from src.workflows.routers.history_router import route_history_save
from src.workflows.routers.message_router import route_message
from src.workflows.subgraphs.area_loop.graph import (
    MAX_AREA_RECURSION,
    build_area_graph,
)
from src.workflows.subgraphs.transcribe.graph import build_transcribe_graph


def _add_nodes(builder: StateGraph, transcribe_graph, area_graph) -> None:
    """Add all nodes to the workflow graph."""
    builder.add_node("transcribe", transcribe_graph)
    builder.add_node("load_history", load_history)
    builder.add_node("build_user_message", build_user_message)
    builder.add_node(
        "extract_target",
        partial(extract_target, llm=get_llm_extract_target()),
    )
    builder.add_node(
        "interview_analysis",
        partial(interview_analysis, llm=get_llm_interview_analysis()),
    )
    builder.add_node(
        "interview_response",
        partial(interview_response, llm=get_llm_interview_response()),
    )
    builder.add_node("save_history", save_history)
    builder.add_node("area_loop", area_graph)


def _add_edges(builder: StateGraph) -> None:
    """Add all edges to the workflow graph."""
    builder.add_edge(START, "transcribe")
    builder.add_edge("transcribe", "load_history")
    builder.add_edge("load_history", "build_user_message")
    builder.add_edge("build_user_message", "extract_target")
    builder.add_conditional_edges("extract_target", route_message)
    builder.add_edge("interview_analysis", "interview_response")
    builder.add_conditional_edges(
        "interview_response", route_history_save, ["save_history", END]
    )
    builder.add_conditional_edges(
        "area_loop", route_history_save, ["save_history", END]
    )
    builder.add_edge("save_history", END)


def get_graph():
    """Build and compile the main workflow graph.

    Returns:
        Compiled LangGraph workflow
    """
    builder = StateGraph(State)
    transcribe_graph = build_transcribe_graph(get_llm_transcribe())
    area_graph = build_area_graph(get_llm_area_chat()).with_config(
        {"recursion_limit": MAX_AREA_RECURSION}
    )
    _add_nodes(builder, transcribe_graph, area_graph)
    _add_edges(builder)
    return builder.compile()
