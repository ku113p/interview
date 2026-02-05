from typing import Literal

from src.application.state import State


def route_history_save(state: State) -> Literal["save_history", "__end__"]:
    if state.success is True and state.messages_to_save:
        return "save_history"
    return "__end__"
