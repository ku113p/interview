"""Leaf interview subgraph routers."""

from typing import Literal

from langchain_core.messages import HumanMessage

from src.shared.messages import filter_tool_messages
from src.workflows.subgraphs.leaf_interview.state import LeafInterviewState


def route_after_context_load(
    state: LeafInterviewState,
) -> Literal[
    "create_turn_summary", "generate_leaf_response", "completed_area_response"
]:
    """Route based on interview state after context load.

    - All leaves done or area extracted → completed_area_response
    - First turn (no user message yet) → generate_leaf_response (ask first question)
    - Subsequent turns → create_turn_summary → quick_evaluate
    """
    if state.all_leaves_done or state.area_already_extracted:
        return "completed_area_response"

    current_messages = filter_tool_messages(state.messages)
    has_user_message = any(isinstance(m, HumanMessage) for m in current_messages)

    if not has_user_message:
        return "generate_leaf_response"

    return "create_turn_summary"
