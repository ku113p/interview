from typing import Literal

from .state import AreaState

# Max tool iterations per area loop (prevents infinite loops)
MAX_LOOP_STEPS = 3
# Max recursion depth: 2 * (MAX_LOOP_STEPS + 1) + 1
# Accounts for tool call/response cycle + routing overhead
MAX_AREA_RECURSION = 2 * (MAX_LOOP_STEPS + 1) + 1


def route_area(state: AreaState) -> Literal["area_tools", "area_end"]:
    tool_calls = getattr(state.messages[-1], "tool_calls", None)
    if tool_calls and len(tool_calls) > 0:
        return "area_tools"
    return "area_end"
