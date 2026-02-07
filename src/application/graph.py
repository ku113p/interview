from functools import partial

from langgraph.graph import END, START, StateGraph

from src.application.state import State
from src.config.settings import (
    MAX_TOKENS_CHAT,
    MAX_TOKENS_STRUCTURED,
    MAX_TOKENS_TRANSCRIPTION,
    MODEL_AREA_CHAT,
    MODEL_AUDIO_TRANSCRIPTION,
    MODEL_EXTRACT_TARGET,
    MODEL_INTERVIEW_ANALYSIS,
    MODEL_INTERVIEW_RESPONSE,
)
from src.infrastructure.ai import NewAI
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
        partial(
            extract_target,
            llm=NewAI(
                MODEL_EXTRACT_TARGET, temperature=0, max_tokens=MAX_TOKENS_STRUCTURED
            ).build(),
        ),
    )
    builder.add_node(
        "interview_analysis",
        partial(
            interview_analysis,
            llm=NewAI(
                MODEL_INTERVIEW_ANALYSIS, max_tokens=MAX_TOKENS_STRUCTURED
            ).build(),
        ),
    )
    builder.add_node(
        "interview_response",
        partial(
            interview_response,
            llm=NewAI(MODEL_INTERVIEW_RESPONSE, max_tokens=MAX_TOKENS_CHAT).build(),
        ),
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
    transcribe_graph = build_transcribe_graph(
        NewAI(
            MODEL_AUDIO_TRANSCRIPTION,
            temperature=0,
            max_tokens=MAX_TOKENS_TRANSCRIPTION,
        ).build()
    )
    area_graph = build_area_graph(
        NewAI(MODEL_AREA_CHAT, max_tokens=MAX_TOKENS_CHAT).build()
    ).with_config({"recursion_limit": MAX_AREA_RECURSION})
    _add_nodes(builder, transcribe_graph, area_graph)
    _add_edges(builder)
    return builder.compile()
