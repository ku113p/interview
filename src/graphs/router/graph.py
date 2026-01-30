import enum
from typing import Literal
from typing_extensions import TypedDict

from langgraph.graph import START, StateGraph, END

from src.domain import message, user
from .interview.node import interview
from .area.graph import get_subgraph as area_subgraph


class Target(enum.Enum):
    interview = 'interview' 
    areas = 'areas' 

    @classmethod
    def from_user_mode(cls, mode: user.InputMode):
        match mode:
            case user.InputMode.interview:
                return cls.interview
            case user.InputMode.areas:
                return cls.areas
            case _:
                raise NotImplementedError()


class State(TypedDict):
    user: user.User
    last_messages: list[message.ClientMessage]
    target: Target


def route_message(state: State) -> Literal["area", "interview"]:
    target = state["target"]
    if target == Target.interview:
        return "interview"
    if target == Target.areas:
        return "area"
    
    raise ValueError(f"Unknown target: {target}")


def get_subgraph():
    builder = StateGraph(State)

    builder.add_node("interview", interview)
    builder.add_node("area", area_subgraph())

    builder.add_conditional_edges(
        START,
        route_message,
        ["interview", "area"]
    )
    builder.add_edge("interview", END)
    builder.add_edge("area", END)

    graph = builder.compile()

    return graph