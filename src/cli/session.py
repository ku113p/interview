import asyncio
import tempfile
import uuid
from typing import BinaryIO, cast

from langchain_core.messages import BaseMessage

from src import db
from src.domain import message, user
from src.graph import get_graph
from src.state import State, Target

HELP_TEXT = """Commands:
  /help  Show this help
  /exit  Exit the session

Type your message and press Enter to continue.
"""


def parse_user_id(value: str | None) -> uuid.UUID:
    if value is None:
        return uuid.uuid4()
    return uuid.UUID(value)


def ensure_user(user_id: uuid.UUID) -> user.User:
    existing = db.UsersManager.get_by_id(user_id)
    if existing is not None:
        return user.User(id=existing.id, mode=user.InputMode(existing.mode))

    user_obj = user.User(id=user_id, mode=user.InputMode.auto)
    db.UsersManager.create(
        user_obj.id,
        db.User(id=user_obj.id, name="cli", mode=user_obj.mode.value),
    )
    return user_obj


def format_ai_response(messages: list[BaseMessage]) -> str:
    if not messages:
        return ""
    last_msg = messages[-1]
    content = last_msg.content
    if isinstance(content, list):
        return "".join(str(part) for part in content)
    if isinstance(content, str):
        return content
    return str(content)


async def run_graph(state: State) -> dict:
    graph = get_graph()
    result = await graph.ainvoke(state)
    if isinstance(result, dict):
        return result
    return result.model_dump()


def _prompt_user_input() -> str | None:
    try:
        return input("> ").strip()
    except EOFError:
        return None


def _handle_command(user_input: str) -> bool | None:
    if not user_input:
        return None
    if user_input == "/exit":
        return True
    if user_input == "/help":
        print(HELP_TEXT)
        return None
    return False


def _create_state_with_tempfiles(
    user_obj: user.User,
    user_input: str,
) -> tuple[State, list]:
    media_tmp = tempfile.NamedTemporaryFile()
    audio_tmp = tempfile.NamedTemporaryFile()
    media_file = cast(BinaryIO, media_tmp.file)
    audio_file = cast(BinaryIO, audio_tmp.file)
    state = State(
        user=user_obj,
        message=message.ClientMessage(data=user_input),
        media_file=media_file,
        audio_file=audio_file,
        text=user_input,
        target=Target.interview,
        messages=[],
        messages_to_save=[],
        success=None,
        area_id=uuid.uuid4(),
        extract_data_tasks=asyncio.Queue(),
        was_covered=False,
    )
    return state, [media_tmp, audio_tmp]


def _close_tempfiles(tempfiles: list) -> None:
    for temp_file in tempfiles:
        temp_file.close()


async def _handle_message(user_obj: user.User, user_input: str) -> str:
    state, tempfiles = _create_state_with_tempfiles(user_obj, user_input)
    try:
        result = await run_graph(state)
    except KeyError as exc:
        raise RuntimeError(
            "Missing required environment variable. Set OPENAI_API_KEY."
        ) from exc
    finally:
        _close_tempfiles(tempfiles)

    messages: list[BaseMessage] = result.get("messages", [])
    ai_response = format_ai_response(messages)
    return ai_response if ai_response else "(no response)"


async def run_cli_async(user_id: uuid.UUID) -> None:
    user_obj = ensure_user(user_id)
    print(f"User: {user_obj.id}")
    print("Type /help for commands.\n")

    while True:
        user_input = _prompt_user_input()
        if user_input is None:
            break
        command_result = _handle_command(user_input)
        if command_result is True:
            break
        if command_result is None:
            continue
        ai_response = await _handle_message(user_obj, user_input)
        print(ai_response)
