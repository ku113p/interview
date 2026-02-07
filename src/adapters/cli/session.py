import asyncio
import logging
import unicodedata
import uuid

from src.application.workers import Runtime
from src.domain import ClientMessage, InputMode, User
from src.infrastructure.db import repositories as db
from src.shared.ids import new_id

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


async def _prompt_user_input() -> str | None:
    """Prompt for user input without blocking the event loop."""
    loop = asyncio.get_event_loop()
    try:
        user_input = await loop.run_in_executor(None, input, "> ")
        return user_input.strip()
    except EOFError:
        return None


def _handle_command(user_input: str) -> bool | None:
    """Handle CLI commands.

    Returns:
        True: exit command
        None: command handled (help) or empty input, continue loop
        False: not a command, process as message
    """
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
    """Validate user input. Returns error message or None if valid."""
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


async def _process_user_input(user_input: str, runtime: Runtime) -> None:
    """Process a single user input and print the response."""
    normalized_input = _normalize_user_input(user_input).strip()
    validation_error = _validate_user_input(normalized_input)
    if validation_error:
        logger.info("Rejected user input", extra={"length": len(normalized_input)})
        print(f"Error: {validation_error}")
        return

    msg = ClientMessage(data=normalized_input)
    response = await runtime.send_and_receive(msg)
    print(response)


async def _run_cli_loop(runtime: Runtime) -> None:
    """Main CLI input loop."""
    while True:
        user_input = await _prompt_user_input()
        if user_input is None:
            break
        command_result = _handle_command(user_input)
        if command_result is True:
            break
        if command_result is None:
            continue
        await _process_user_input(user_input, runtime)


async def run_cli_async(user_id: uuid.UUID) -> None:
    """Run the CLI session."""
    user_obj = ensure_user(user_id)
    logger.info("Starting CLI session", extra={"user_id": str(user_obj.id)})
    print(f"User: {user_obj.id}")
    print("Type /help for commands.\n")

    async with Runtime(user_obj) as runtime:
        await _run_cli_loop(runtime)
