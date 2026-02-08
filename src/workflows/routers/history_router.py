from typing import Literal

from src.application.state import State


def route_on_success(state: State) -> Literal["save_history", "__end__"]:
    if state.is_successful is True and state.messages_to_save:
        return "save_history"
    return "__end__"
