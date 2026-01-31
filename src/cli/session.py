import asyncio
import secrets
import sys
import time
import uuid
from typing import Protocol, cast

from langchain_core.messages import AIMessage, BaseMessage  # type: ignore[import]

from src import graph
from src.domain import message, user


def _generate_user_id() -> uuid.UUID:
    if hasattr(uuid, "uuid7"):
        return uuid.uuid7()

    timestamp_ms = int(time.time() * 1000) & ((1 << 48) - 1)
    rand_a = secrets.randbits(12)
    rand_b = secrets.randbits(62)

    value = timestamp_ms << 80
    value |= 0x7 << 76
    value |= rand_a << 64
    value |= 0b10 << 62
    value |= rand_b & ((1 << 62) - 1)

    return uuid.UUID(int=value)


State = graph.State


class GraphRunner(Protocol):
    async def __call__(self, state: State) -> State: ...


def build_initial_state(user_obj: user.User | None = None) -> State:
    resolved_user = user_obj or user.User(
        id=_generate_user_id(), mode=user.InputMode.auto
    )
    base_state = cast(
        State,
        {
            "user": resolved_user,
            "message": message.ClientMessage(data=""),
        },
    )
    updates = graph.init_state(base_state)
    return cast(State, base_state | updates)


def inject_user_text(state: State, content: str) -> State:
    next_state = dict(state)
    next_state["message"] = message.ClientMessage(data=content)
    next_state["loop_step"] = state.get("loop_step", 0) + 1
    return cast(State, next_state)


async def run_turn(
    runner: GraphRunner, state: State, content: str
) -> tuple[State, str]:
    next_state = inject_user_text(state, content)
    result = await runner(next_state)
    messages = result.get("messages")
    if messages is None:
        raise ValueError("Graph returned no messages")
    reply = extract_latest_response(cast(list[BaseMessage], messages))
    return result, reply


def extract_latest_response(messages: list[BaseMessage]) -> str:
    for entry in reversed(messages):
        if isinstance(entry, AIMessage):
            return entry.content
    raise ValueError("No assistant response found")


def run_cli(runner: GraphRunner, user_obj: user.User | None = None) -> None:
    initial_state = build_initial_state(user_obj)
    asyncio.run(cli_loop(runner, initial_state))


async def cli_loop(runner: GraphRunner, state: State) -> None:
    current_state = state
    while True:
        text = read_cli_line()
        if text is None:
            break
        if not text:
            continue
        current_state = await execute_turn(runner, current_state, text)


async def execute_turn(runner: GraphRunner, state: State, text: str) -> State:
    try:
        next_state, reply = await run_turn(runner, state, text)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return state
    print(reply)
    return next_state


def read_cli_line() -> str | None:
    try:
        line = input("> ").strip()
    except EOFError:
        return None
    except KeyboardInterrupt:
        print()
        return None
    if line == "/exit":
        return None
    return line
