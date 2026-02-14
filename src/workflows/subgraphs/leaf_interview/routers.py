"""Leaf interview subgraph routers."""

from typing import Literal

from src.workflows.subgraphs.leaf_interview.state import LeafInterviewState


def route_after_context_load(
    state: LeafInterviewState,
) -> Literal["quick_evaluate", "completed_area_response"]:
    """Route based on whether all leaves are done or area was extracted."""
    if state.all_leaves_done or state.area_already_extracted:
        return "completed_area_response"
    return "quick_evaluate"
