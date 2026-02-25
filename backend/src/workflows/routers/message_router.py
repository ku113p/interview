from typing import Literal

from src.processes.interview import State, Target


def route_by_target(
    state: State,
) -> Literal["area_loop", "leaf_interview", "small_talk_response"]:
    """Route based on extracted target intent."""
    target = state.target
    if target == Target.conduct_interview:
        return "leaf_interview"
    if target == Target.manage_areas:
        return "area_loop"
    if target == Target.small_talk:
        return "small_talk_response"

    raise ValueError(f"Unknown target: {target}")
