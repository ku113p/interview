"""Router for command handling in the main workflow."""

from typing import Literal

from src.processes.interview import State


def route_on_command(state: State) -> Literal["load_history", "__end__"]:
    """Route based on whether a command was handled.

    If command_response is set, the command was processed and we end.
    Otherwise, continue to load_history for normal workflow.
    """
    if state.command_response is not None:
        return "__end__"
    return "load_history"
