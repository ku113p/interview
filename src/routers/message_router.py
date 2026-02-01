import enum
from typing import Literal
from typing_extensions import TypedDict

from src.domain import user


class Target(enum.Enum):
    interview = "interview"
    areas = "areas"

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
    target: Target


def route_message(state: State) -> Literal["area_chat", "interview"]:
    target = state["target"]
    if target == Target.interview:
        return "interview"
    if target == Target.areas:
        return "area_chat"

    raise ValueError(f"Unknown target: {target}")
