from typing import Literal

from src.application.state import State, Target


def route_by_target(state: State) -> Literal["area_loop", "interview_analysis"]:
    target = state.target
    if target == Target.interview:
        return "interview_analysis"
    if target == Target.areas:
        return "area_loop"

    raise ValueError(f"Unknown target: {target}")
