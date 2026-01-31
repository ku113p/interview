import uuid
from typing import cast

import pytest
from langchain_core.messages import AIMessage

from src.cli import session
from src.domain import user


def build_base_state() -> session.State:
    state = session.build_initial_state(
        user.User(id=uuid.uuid4(), mode=user.InputMode.auto)
    )
    state = cast(session.State, state | {"messages": []})
    return state


def test_build_initial_state_provides_defaults():
    state = session.build_initial_state()
    assert "user" in state
    assert "message" in state
    assert "messages" in state
    messages = state["messages"]
    assert isinstance(messages, list)


@pytest.mark.anyio
async def test_run_turn_returns_reply():
    state = build_base_state()

    async def runner(state: session.State) -> session.State:
        updated = dict(state)
        updated["messages"] = [AIMessage(content="ok", tool_calls=[])]
        return cast(session.State, updated)

    result, reply = await session.run_turn(runner, state, "hello")
    assert reply == "ok"
    assert result["message"].data == "hello"


@pytest.mark.anyio
async def test_run_turn_raises_without_messages():
    state = build_base_state()

    async def runner(state: session.State) -> session.State:
        return cast(session.State, dict(state))

    with pytest.raises(ValueError):
        await session.run_turn(runner, state, "hello")


def test_extract_latest_response_picks_last():
    first = AIMessage(content="a", tool_calls=[])
    second = AIMessage(content="b", tool_calls=[])
    result = session.extract_latest_response([first, second])
    assert result == "b"
