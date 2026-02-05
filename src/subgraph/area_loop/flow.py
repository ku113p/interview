from typing import Literal

MAX_LOOP_STEPS = 3
MAX_AREA_RECURSION = 2 * (MAX_LOOP_STEPS + 1) + 1


def route_area(state: dict) -> Literal["area_tools", "area_end"]:
    tool_calls = getattr(state["messages"][-1], "tool_calls", None)
    if tool_calls and len(tool_calls) > 0:
        return "area_tools"
    return "area_end"
