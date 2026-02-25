"""Leaf interview subgraph definition."""

from functools import partial

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from src.workflows.subgraphs.leaf_interview.nodes import (
    completed_area_response,
    create_turn_summary,
    generate_leaf_response,
    load_interview_context,
    quick_evaluate,
    select_next_leaf,
    update_coverage_status,
)
from src.workflows.subgraphs.leaf_interview.routers import route_after_context_load
from src.workflows.subgraphs.leaf_interview.state import LeafInterviewState


def _add_nodes(
    builder: StateGraph, llm_evaluate: ChatOpenAI, llm_response: ChatOpenAI
) -> None:
    """Register all nodes on the graph builder."""
    builder.add_node("load_interview_context", load_interview_context)
    builder.add_node(
        "create_turn_summary", partial(create_turn_summary, llm=llm_response)
    )
    builder.add_node("quick_evaluate", partial(quick_evaluate, llm=llm_evaluate))
    builder.add_node(
        "update_coverage_status", partial(update_coverage_status, llm=llm_response)
    )
    builder.add_node("select_next_leaf", select_next_leaf)
    builder.add_node(
        "generate_leaf_response", partial(generate_leaf_response, llm=llm_response)
    )
    builder.add_node(
        "completed_area_response", partial(completed_area_response, llm=llm_response)
    )


def _add_edges(builder: StateGraph) -> None:
    """Wire all edges on the graph builder."""
    builder.add_edge(START, "load_interview_context")
    builder.add_conditional_edges(
        "load_interview_context",
        route_after_context_load,
        ["create_turn_summary", "generate_leaf_response", "completed_area_response"],
    )
    builder.add_edge("create_turn_summary", "quick_evaluate")
    builder.add_edge("quick_evaluate", "update_coverage_status")
    builder.add_edge("update_coverage_status", "select_next_leaf")
    builder.add_edge("select_next_leaf", "generate_leaf_response")
    builder.add_edge("generate_leaf_response", END)
    builder.add_edge("completed_area_response", END)


def build_leaf_interview_graph(llm_evaluate: ChatOpenAI, llm_response: ChatOpenAI):
    """Build and compile the leaf interview subgraph."""
    builder = StateGraph(LeafInterviewState)
    _add_nodes(builder, llm_evaluate, llm_response)
    _add_edges(builder)
    return builder.compile()
