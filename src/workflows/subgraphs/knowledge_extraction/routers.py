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
    if not state.sub_area_paths or not state.messages:
        return "__end__"
    return "extract_summaries"


def route_extraction_success(
    state: KnowledgeExtractionState,
) -> Literal["save_summary", "__end__"]:
    """Route after extract_summaries - continue only if successful.

    Returns:
        "save_summary" if extraction succeeded, "__end__" otherwise.
    """
    if not state.is_successful or not state.extracted_summary:
        return "__end__"
    return "save_summary"
