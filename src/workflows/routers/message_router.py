from typing import Literal

from src.processes.interview import State, Target


def route_by_target(
    state: State,
) -> Literal["area_loop", "load_interview_context", "small_talk_response"]:
    """Route based on extracted target intent."""
    target = state.target
    if target == Target.conduct_interview:
        return "load_interview_context"
    if target == Target.manage_areas:
        return "area_loop"
    if target == Target.small_talk:
        return "small_talk_response"

    raise ValueError(f"Unknown target: {target}")


def route_after_context_load(
    state: State,
) -> Literal["quick_evaluate", "completed_area_response"]:
    """Route based on whether all leaves are done or area was extracted."""
    # If all leaves are done (no sub-areas or all covered/skipped)
    if state.all_leaves_done:
        return "completed_area_response"
    # If area was already extracted (shouldn't happen in new flow, but safety check)
    if state.area_already_extracted:
        return "completed_area_response"
    return "quick_evaluate"
