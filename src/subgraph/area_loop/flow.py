from typing import Literal


MAX_LOOP_STEPS = 3
MAX_AREA_RECURSION = 2 * (MAX_LOOP_STEPS + 1) + 1


def route_area(state: dict) -> Literal["area_threshold", "area_tools", "area_end"]:
    if state["messages"][-1].tool_calls:
        return "area_tools"
    return "area_end"
