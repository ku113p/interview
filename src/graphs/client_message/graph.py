from typing import Literal
from typing_extensions import TypedDict

from langgraph.graph import START, StateGraph, END

from src.domain import message, user
from .audio_extractor import extract_audio
from .target_extractor import extract_target
from .text_extractor import extract_text


class State(TypedDict):
    user: user.User
    message: message.ClientMessage


def route_message(state: State) -> Literal["extract_audio", "extract_text"]:
    c_msg = state["message"]
    if isinstance(c_msg.data, str):
        return "extract_text"
    return "extract_audio"


def get_subgraph():
    builder = StateGraph(State)

    builder.add_node("extract_audio", extract_audio)
    builder.add_node("extract_text", extract_text)
    builder.add_node("extract_target", extract_target)

    builder.add_conditional_edges(
        START,
        route_message,
        ["extract_audio", "extract_text"]
    )
    builder.add_edge("extract_audio", "extract_text")
    builder.add_edge("extract_text", "extract_target")
    builder.add_edge("extract_target", END)

    graph = builder.compile()

    return graph