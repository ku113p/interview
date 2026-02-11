from typing import Literal

from src.processes.interview import State, Target


def route_by_target(
    state: State,
) -> Literal["area_loop", "interview_analysis", "small_talk_response"]:
    target = state.target
    if target == Target.conduct_interview:
        return "interview_analysis"
    if target == Target.manage_areas:
        return "area_loop"
    if target == Target.small_talk:
        return "small_talk_response"

    raise ValueError(f"Unknown target: {target}")


def route_after_analysis(
    state: State,
) -> Literal["interview_response", "completed_area_response"]:
    """Route based on whether area was already extracted."""
    if state.area_already_extracted:
        return "completed_area_response"
    return "interview_response"
