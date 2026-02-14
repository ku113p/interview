"""Leaf interview subgraph definition."""

from functools import partial

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from src.workflows.subgraphs.leaf_interview.nodes import (
    completed_area_response,
    generate_leaf_response,
    load_interview_context,
    quick_evaluate,
    select_next_leaf,
    update_coverage_status,
)
from src.workflows.subgraphs.leaf_interview.routers import route_after_context_load
from src.workflows.subgraphs.leaf_interview.state import LeafInterviewState


def build_leaf_interview_graph(llm_evaluate: ChatOpenAI, llm_response: ChatOpenAI):
    """Build and compile the leaf interview subgraph."""
    builder = StateGraph(LeafInterviewState)

    # Add nodes
    builder.add_node("load_interview_context", load_interview_context)
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

    # Entry point
    builder.add_edge(START, "load_interview_context")

    # Route after context load
    builder.add_conditional_edges(
        "load_interview_context",
        route_after_context_load,
        ["quick_evaluate", "completed_area_response"],
    )

    # Interview flow
    builder.add_edge("quick_evaluate", "update_coverage_status")
    builder.add_edge("update_coverage_status", "select_next_leaf")
    builder.add_edge("select_next_leaf", "generate_leaf_response")
    builder.add_edge("generate_leaf_response", END)

    # Completed area flow
    builder.add_edge("completed_area_response", END)

    return builder.compile()
