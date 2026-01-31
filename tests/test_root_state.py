import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
from typing import cast
import uuid

from langchain_core.messages import AIMessage, BaseMessage
from src import graph
from src.domain import message, user
from src.graphs.router.graph import Target
from src.graphs.deps import Deps


def test_root_init_seeds_defaults():
    state = cast(
        graph.State,
        {
            "user": user.User(id=uuid.uuid4(), mode=user.InputMode.auto),
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


def test_root_init_overrides_none_defaults():
    state = cast(
        graph.State,
        {
            "user": user.User(id=uuid.uuid4(), mode=user.InputMode.auto),
            "message": message.ClientMessage(data="hello"),
            "messages": None,
            "loop_step": None,
            "was_covered": None,
            "media_file": None,
            "audio_file": None,
            "extract_data_dir": None,
        },
    )
    updates = graph.init_state(state)
    assert isinstance(updates["messages"], list)
    assert updates["loop_step"] == 0
    assert updates["was_covered"] is False
    assert updates["media_file"] is not None
    assert updates["audio_file"] is not None
    assert updates["extract_data_dir"] == graph.DEFAULT_SIGNAL_DIR


def test_root_graph_runs_text_message():
    deps, build_log = build_stub_deps()
    state = build_base_state(user.InputMode.auto)
    root_graph = graph.get_graph(deps)
    result = asyncio.run(root_graph.ainvoke(state))
    assert result["text"] == "hello"
    assert result["target"] is not None
    assert isinstance(result["messages"], list)
    assert build_log["count"] > 0


def test_message_flow_accumulates_messages():
    deps, _ = build_stub_deps()
    state = build_base_state(user.InputMode.interview)
    root_graph = graph.get_graph(deps)
    result = asyncio.run(root_graph.ainvoke(state))
    messages = result["messages"]
    assert isinstance(messages, list)
    assert all(isinstance(msg, BaseMessage) for msg in messages)
    assert any(isinstance(msg, AIMessage) for msg in messages)


def build_base_state(mode: user.InputMode):
    base_state = {
        "user": user.User(id=uuid.uuid4(), mode=mode),
        "message": message.ClientMessage(data="hello"),
        "area_id": uuid.uuid4(),
    }
    init_updates = graph.init_state(cast(graph.State, base_state))
    merged = base_state | init_updates
    return cast(graph.State, merged)


def test_client_adapter_preserves_normalized_keys():
    base_state = build_base_state(user.InputMode.auto)
    client_state = graph.adapt_client_state(base_state)
    for key in graph.CLIENT_STATE_KEYS:
        if key in {"text", "target"}:
            continue
        assert key in client_state


def build_stub_deps() -> tuple[Deps, dict[str, int]]:
    call_log = {"count": 0}

    class StubLLM:
        async def ainvoke(self, messages):
            first = messages[0]
            if isinstance(first, dict):
                payload = {"final_answer": "thanks", "all_covered": False}
                return SimpleNamespace(content=json.dumps(payload))
            return SimpleNamespace(content="hello")

        def bind_tools(self, tools):
            async def ainvoke(_):
                return [AIMessage(content="ok", tool_calls=[])]

            return SimpleNamespace(ainvoke=ainvoke)

        def with_structured_output(self, model_cls):
            async def ainvoke(_):
                return model_cls(target=Target.areas)

            return SimpleNamespace(ainvoke=ainvoke)

    def build_llm(temperature: float | None = None):
        call_log["count"] += 1
        return StubLLM()

    def get_area_tools():
        return []

    deps = cast(Deps, {"build_llm": build_llm, "get_area_tools": get_area_tools})
    return deps, call_log
