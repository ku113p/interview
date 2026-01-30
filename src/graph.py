from dataclasses import dataclass
import enum
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, MessagesState, START, END

from .domain import message, user


class Direction(enum.Enum):
    interview = 'interview'
    areas = 'areas'


class State(TypedDict):
    user: user.User
    message: message.ClientMessage
    direction: Direction
    text: str


def extract_direction_and_text(state: State):
    message = state["message"]

    text, filepath = extract_message_text(message, agent)

    match mode := state["user"]["mode"]:
        case user.InputMode.interview:
            direction = Direction.interview
        case user.InputMode.areas:
            direction = Direction.areas
        case user.InputMode.auto:
            direction = extract_direction(text, agent)
        case _:
            raise NotImplementedError()
    
    media_type = None if isinstance(message.data, str) else message.data.type
    save_user_message(state["user"], text, filepath, media_type)

    return state | {"direction": direction}


def extract_message_text(msg: message.ClientMessage, agent) -> tuple[str, str]:
    if isinstance(msg.data, str):
        return msg.data, None
    
    audio_
    if msg.data.type == message.MessageType.video:

    
    return agent.extract_text(msg.data)


def extract_direction(text: str, agent) -> Direction:
    return agent.extract_direction(text)


def save_user_message(user: user.User, text: str, filepath: str, media_type: message.MessageType):
    ...
