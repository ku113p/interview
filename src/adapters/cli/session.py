import asyncio
import logging
import tempfile
import unicodedata
import uuid

from langchain_core.messages import BaseMessage

from src.application.graph import get_graph
from src.application.state import State, Target
from src.domain import ClientMessage, InputMode, User
from src.infrastructure.db import repositories as db
from src.shared.ids import new_id
from src.shared.utils.content import normalize_content

logger = logging.getLogger(__name__)

# Max chars per message (prevents performance issues)
MAX_MESSAGE_LENGTH = 10_000
# ASCII space: minimum allowed character
MIN_PRINTABLE_CHAR = 32

HELP_TEXT = """Commands:
  /help  Show this help
  /exit  Exit the session

Type your message and press Enter to continue.
"""


def parse_user_id(value: str | None) -> uuid.UUID:
    if value is None:
        return new_id()
    return uuid.UUID(value)


def ensure_user(user_id: uuid.UUID) -> User:
    """Get or create user."""
    existing = db.UsersManager.get_by_id(user_id)
    if existing is not None:
        return User(id=existing.id, mode=InputMode(existing.mode))

    user_obj = User(id=user_id, mode=InputMode.auto)
    db.UsersManager.create(
        user_obj.id,
        db.User(id=user_obj.id, name="cli", mode=user_obj.mode.value),
    )
    return user_obj


def get_current_area_id(user_id: uuid.UUID) -> uuid.UUID | None:
    """Get user's current_area_id from database."""
    db_user = db.UsersManager.get_by_id(user_id)
    if db_user is not None:
        return db_user.current_area_id
    return None


def format_ai_response(messages: list[BaseMessage]) -> str:
    if not messages:
        return ""
    last_msg = messages[-1]
    return normalize_content(last_msg.content)


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


def _normalize_user_input(user_input: str) -> str:
    return unicodedata.normalize("NFKC", user_input)


def _validate_user_input(user_input: str) -> str | None:
    if not user_input:
        return "Please type your message"
    if len(user_input) > MAX_MESSAGE_LENGTH:
        return f"Message too long: {len(user_input)}/{MAX_MESSAGE_LENGTH} chars"
    if "\x00" in user_input:
        return "No null characters allowed"
    for char in user_input:
        if ord(char) < MIN_PRINTABLE_CHAR and char not in {"\n", "\r", "\t"}:
            return "No control characters allowed"
    return None


def _create_state_with_tempfiles(
    user_obj: User,
    user_input: str,
    current_area_id: uuid.UUID | None,
) -> tuple[State, list]:
    media_tmp = tempfile.NamedTemporaryFile(delete=False)
    audio_tmp = tempfile.NamedTemporaryFile(delete=False)
    # Use current_area_id if set, otherwise generate a new one
    area_id = current_area_id if current_area_id is not None else new_id()
    state = State(
        user=user_obj,
        message=ClientMessage(data=user_input),
        media_file=media_tmp.name,
        audio_file=audio_tmp.name,
        text=user_input,
        target=Target.interview,
        messages=[],
        messages_to_save={},
        success=None,
        area_id=area_id,
        extract_data_tasks=asyncio.Queue(),
        was_covered=False,
    )
    return state, [media_tmp, audio_tmp]


def _close_tempfiles(tempfiles: list) -> None:
    for temp_file in tempfiles:
        temp_file.close()


async def _handle_message(
    user_obj: User, user_input: str, current_area_id: uuid.UUID | None
) -> str:
    normalized_input = _normalize_user_input(user_input).strip()
    validation_error = _validate_user_input(normalized_input)
    if validation_error:
        logger.info(
            "Rejected user input",
            extra={"user_id": str(user_obj.id), "length": len(normalized_input)},
        )
        return f"Error: {validation_error}"

    return await _process_validated_message(user_obj, normalized_input, current_area_id)


async def _process_validated_message(
    user_obj: User, user_input: str, current_area_id: uuid.UUID | None
) -> str:
    state, tempfiles = _create_state_with_tempfiles(
        user_obj, user_input, current_area_id
    )
    try:
        logger.info(
            "Processing user message",
            extra={"user_id": str(user_obj.id), "length": len(user_input)},
        )
        result = await run_graph(state)
    except RuntimeError as exc:
        if "OPENROUTER_API_KEY" in str(exc):
            raise RuntimeError("Set OPENROUTER_API_KEY environment variable") from exc
        raise
    finally:
        _close_tempfiles(tempfiles)

    messages: list[BaseMessage] = result.get("messages", [])
    return format_ai_response(messages) or "(no response)"


async def _process_user_input(user_obj: User, user_input: str) -> None:
    """Process a single user input and print the response."""
    # Fetch current_area_id fresh (may change via set_current_area tool)
    current_area_id = get_current_area_id(user_obj.id)
    ai_response = await _handle_message(user_obj, user_input, current_area_id)
    print(ai_response)


async def run_cli_async(user_id: uuid.UUID) -> None:
    user_obj = ensure_user(user_id)
    logger.info("Starting CLI session", extra={"user_id": str(user_obj.id)})
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
        await _process_user_input(user_obj, user_input)
