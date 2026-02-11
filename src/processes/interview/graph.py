from functools import partial

from langgraph.graph import END, START, StateGraph

from src.infrastructure.llms import (
    get_llm_area_chat,
    get_llm_extract_target,
    get_llm_interview_analysis,
    get_llm_interview_response,
    get_llm_small_talk,
    get_llm_transcribe,
)
from src.processes.interview.state import State
from src.workflows.nodes.commands.handle_command import handle_command
from src.workflows.nodes.input.build_user_message import build_user_message
from src.workflows.nodes.input.extract_target import extract_target
from src.workflows.nodes.persistence.save_history import save_history
from src.workflows.nodes.processing.completed_area_response import (
    completed_area_response,
)
from src.workflows.nodes.processing.interview_analysis import interview_analysis
from src.workflows.nodes.processing.interview_response import interview_response
from src.workflows.nodes.processing.load_history import load_history
from src.workflows.nodes.processing.small_talk_response import small_talk_response
from src.workflows.routers.command_router import route_on_command
from src.workflows.routers.history_router import route_on_success
from src.workflows.routers.message_router import route_after_analysis, route_by_target
from src.workflows.subgraphs.area_loop.graph import (
    MAX_AREA_RECURSION,
    build_area_graph,
)
from src.workflows.subgraphs.transcribe.graph import build_transcribe_graph


def _add_workflow_nodes(builder: StateGraph, transcribe_graph, area_graph) -> None:
    """Add all nodes to the main workflow graph."""
    builder.add_node("transcribe", transcribe_graph)
    builder.add_node("handle_command", handle_command)
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
    builder.add_node(
        "small_talk_response",
        partial(small_talk_response, llm=get_llm_small_talk()),
    )
    builder.add_node(
        "completed_area_response",
        partial(completed_area_response, llm=get_llm_small_talk()),
    )
    builder.add_node("save_history", save_history)
    builder.add_node("area_loop", area_graph)


def _add_workflow_edges(builder: StateGraph) -> None:
    """Add all edges to the main workflow graph."""
    builder.add_edge(START, "transcribe")
    builder.add_edge("transcribe", "handle_command")
    builder.add_conditional_edges(
        "handle_command", route_on_command, ["load_history", END]
    )
    builder.add_edge("load_history", "build_user_message")
    builder.add_edge("build_user_message", "extract_target")
    builder.add_conditional_edges("extract_target", route_by_target)
    builder.add_conditional_edges("interview_analysis", route_after_analysis)
    builder.add_conditional_edges(
        "interview_response", route_on_success, ["save_history", END]
    )
    builder.add_conditional_edges(
        "completed_area_response", route_on_success, ["save_history", END]
    )
    builder.add_conditional_edges(
        "small_talk_response", route_on_success, ["save_history", END]
    )
    builder.add_conditional_edges("area_loop", route_on_success, ["save_history", END])
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
    _add_workflow_nodes(builder, transcribe_graph, area_graph)
    _add_workflow_edges(builder)
    return builder.compile()
