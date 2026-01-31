import asyncio
from pathlib import Path
from typing import cast
import uuid

from langchain_core.messages import BaseMessage
from src import graph
from src.domain import message, user


def test_root_init_seeds_defaults():
    state = cast(
        graph.State,
        {
            "user": user.User(id=uuid.uuid7(), mode=user.InputMode.auto),
            "message": message.ClientMessage(data="hello"),
        },
    )
    updates = graph.init_state(state)
    assert updates["loop_step"] == 0
    assert updates["was_covered"] is False
    assert updates["extract_data_dir"].endswith("signals")
    assert isinstance(updates["messages"], list)
    assert updates["media_file"] is not None
    assert updates["audio_file"] is not None
    assert Path(updates["extract_data_dir"]).exists()


def test_root_graph_runs_text_message():
    state = cast(
        graph.State,
        {
            "user": user.User(id=uuid.uuid7(), mode=user.InputMode.auto),
            "message": message.ClientMessage(data="hello"),
        },
    )
    graph_obj = graph.get_graph()
    result = graph_obj.invoke(state)
    assert result["text"] == "hello"
    assert result["target"] is not None
    assert isinstance(result["messages"], list)


def test_message_flow_accumulates_messages():
    state = cast(
        graph.State,
        {
            "user": user.User(id=uuid.uuid7(), mode=user.InputMode.interview),
            "message": message.ClientMessage(data="hi"),
        },
    )
    graph_obj = graph.get_graph()
    result = graph_obj.invoke(state)
    messages = result["messages"]
    assert isinstance(messages, list)
    assert all(isinstance(msg, BaseMessage) for msg in messages)
