import tempfile
import uuid
from pathlib import Path
from tempfile import _TemporaryFileWrapper
from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import NotRequired, TypedDict

from src.domain import message, user
from src.graphs.client_message.graph import get_subgraph as client_message_subgraph
from src.graphs.router.graph import Target
from src.graphs.router.graph import get_subgraph as router_subgraph


class State(TypedDict):
    user: user.User
    message: message.ClientMessage
    messages: Annotated[list[BaseMessage], add_messages]
    loop_step: int
    extract_data_dir: str
    was_covered: bool
    text: NotRequired[str]
    target: NotRequired[Target]
    area_id: NotRequired[uuid.UUID]
    media_file: NotRequired[_TemporaryFileWrapper[bytes]]
    audio_file: NotRequired[_TemporaryFileWrapper[bytes]]


DEFAULT_SIGNAL_DIR = "signals"


def init_state(state: State):
    updates = missing_state_defaults(state)
    ensure_signal_dir(updates.get("extract_data_dir", state.get("extract_data_dir")))
    return updates


def missing_state_defaults(state: State):
    updates = {}
    if "messages" not in state:
        updates["messages"] = []
    if "media_file" not in state:
        updates["media_file"] = build_temp_file()
    if "audio_file" not in state:
        updates["audio_file"] = build_temp_file()
    if "loop_step" not in state:
        updates["loop_step"] = 0
    if "was_covered" not in state:
        updates["was_covered"] = False
    if "extract_data_dir" not in state:
        updates["extract_data_dir"] = DEFAULT_SIGNAL_DIR
    return updates


def build_temp_file() -> _TemporaryFileWrapper[bytes]:
    return tempfile.NamedTemporaryFile()


def ensure_signal_dir(path: str | None) -> str:
    if path is None:
        raise ValueError("Signal directory is required")
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def get_graph():
    builder = StateGraph(State)
    builder.add_node("init", init_state)
    builder.add_node("client_message", client_message_subgraph())
    builder.add_node("router", router_subgraph())
    builder.add_edge(START, "init")
    builder.add_edge("init", "client_message")
    builder.add_edge("client_message", "router")
    builder.add_edge("router", END)
    return builder.compile()
