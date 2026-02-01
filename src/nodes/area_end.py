from typing_extensions import TypedDict


class State(TypedDict):
    messages: list


def area_end(state: State):
    return state
