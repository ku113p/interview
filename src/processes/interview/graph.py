from functools import partial

from langgraph.graph import END, START, StateGraph

from src.infrastructure.llms import (
    get_llm_area_chat,
    get_llm_extract_target,
    get_llm_leaf_response,
    get_llm_quick_evaluate,
    get_llm_small_talk,
    get_llm_transcribe,
)
from src.processes.interview.state import State
from src.workflows.nodes.commands.handle_command import handle_command
from src.workflows.nodes.input.build_user_message import build_user_message
from src.workflows.nodes.input.extract_target import extract_target
from src.workflows.nodes.persistence.save_history import save_history
from src.workflows.nodes.processing.load_history import load_history
from src.workflows.nodes.processing.small_talk_response import small_talk_response
from src.workflows.routers.command_router import route_on_command
from src.workflows.routers.history_router import route_on_success
from src.workflows.routers.message_router import route_by_target
from src.workflows.subgraphs.area_loop.graph import (
    MAX_AREA_RECURSION,
    build_area_graph,
)
from src.workflows.subgraphs.leaf_interview import build_leaf_interview_graph
from src.workflows.subgraphs.transcribe.graph import build_transcribe_graph


def _add_input_nodes(builder: StateGraph, transcribe_graph) -> None:
    """Add input processing nodes."""
    builder.add_node("transcribe", transcribe_graph)
    builder.add_node("handle_command", handle_command)
    builder.add_node("load_history", load_history)
    builder.add_node("build_user_message", build_user_message)
    builder.add_node(
        "extract_target", partial(extract_target, llm=get_llm_extract_target())
    )


def _add_response_nodes(builder: StateGraph, area_graph, leaf_interview_graph) -> None:
    """Add response and output nodes."""
    builder.add_node(
        "small_talk_response", partial(small_talk_response, llm=get_llm_small_talk())
    )
    builder.add_node("save_history", save_history)
    builder.add_node("area_loop", area_graph)
    builder.add_node("leaf_interview", leaf_interview_graph)


def _add_workflow_nodes(
    builder: StateGraph, transcribe_graph, area_graph, leaf_interview_graph
) -> None:
    """Add all nodes to the main workflow graph."""
    _add_input_nodes(builder, transcribe_graph)
    _add_response_nodes(builder, area_graph, leaf_interview_graph)


def _add_input_edges(builder: StateGraph) -> None:
    """Add input processing edges (transcribe → extract_target)."""
    builder.add_edge(START, "transcribe")
    builder.add_edge("transcribe", "handle_command")
    builder.add_conditional_edges(
        "handle_command", route_on_command, ["load_history", END]
    )
    builder.add_edge("load_history", "build_user_message")
    builder.add_edge("build_user_message", "extract_target")
    builder.add_conditional_edges("extract_target", route_by_target)


def _add_output_edges(builder: StateGraph) -> None:
    """Add response → save_history → END edges."""
    builder.add_conditional_edges(
        "leaf_interview", route_on_success, ["save_history", END]
    )
    builder.add_conditional_edges(
        "small_talk_response", route_on_success, ["save_history", END]
    )
    builder.add_conditional_edges("area_loop", route_on_success, ["save_history", END])
    builder.add_edge("save_history", END)


def _add_workflow_edges(builder: StateGraph) -> None:
    """Add all edges to the main workflow graph."""
    _add_input_edges(builder)
    _add_output_edges(builder)


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
    # leaf_interview subgraph uses LeafInterviewState which maps to/from State:
    # - Input: user, area_id, messages, area_already_extracted
    # - Output: messages_to_save, is_successful, completed_leaf_id, is_fully_covered,
    #           active_leaf_id, question_text, turn_summary_text, set_covered_at
    leaf_interview_graph = build_leaf_interview_graph(
        get_llm_quick_evaluate(),
        get_llm_leaf_response(),
    )
    _add_workflow_nodes(builder, transcribe_graph, area_graph, leaf_interview_graph)
    _add_workflow_edges(builder)
    return builder.compile()
