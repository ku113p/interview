"""Routers for extract_data workflow."""

from typing import Literal

from .state import KnowledgeExtractionState


def route_has_data(
    state: KnowledgeExtractionState,
) -> Literal["extract_summaries", "__end__"]:
    """Route after load_area_data - skip if no data to process.

    Returns:
        "extract_summaries" if there is data to extract, "__end__" otherwise.
    """
    # If using pre-extracted leaf summaries, proceed to extract_summaries
    # (which will skip LLM and use the summaries directly)
    if state.use_leaf_summaries and state.extracted_summary:
        return "extract_summaries"
    # Legacy path: need sub_area_paths and messages
    if not state.sub_area_paths or not state.messages:
        return "__end__"
    return "extract_summaries"


def route_extraction_success(
    state: KnowledgeExtractionState,
) -> Literal["prepare_summary", "__end__"]:
    """Route after extract_summaries - continue only if successful.

    Returns:
        "prepare_summary" if extraction succeeded, "__end__" otherwise.
    """
    if not state.is_successful or not state.extracted_summary:
        return "__end__"
    return "prepare_summary"
