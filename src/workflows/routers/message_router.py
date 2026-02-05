from typing import Literal

from src.application.state import State, Target


def route_message(state: State) -> Literal["area_loop", "interview"]:
    target = state.target
    if target == Target.interview:
        return "interview"
    if target == Target.areas:
        return "area_loop"

    raise ValueError(f"Unknown target: {target}")
