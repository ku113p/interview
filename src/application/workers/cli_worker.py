"""CLI worker for handling stdin/stdout communication."""

import asyncio
import logging
import unicodedata
import uuid

from src.application.workers.channels import ChannelRequest, Channels
from src.domain import ClientMessage, InputMode, User
from src.infrastructure.db import managers as db
from src.shared.ids import new_id

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 10_000
MIN_PRINTABLE_CHAR = 32

HELP_TEXT = """Commands:
  /help  Show this help
  /exit  Exit the session

Type your message and press Enter to continue.
"""


def parse_user_id(value: str | None) -> uuid.UUID:
    """Parse user ID from string or generate a new one."""
    return new_id() if value is None else uuid.UUID(value)


def get_or_create_user(user_id: uuid.UUID) -> User:
    """Get or create user."""
    existing = db.UsersManager.get_by_id(user_id)
    if existing is not None:
        return User(id=existing.id, mode=InputMode(existing.mode))
    user_obj = User(id=user_id, mode=InputMode.auto)
    db.UsersManager.create(
        user_obj.id, db.User(id=user_obj.id, name="cli", mode=user_obj.mode.value)
    )
    return user_obj


def _has_control_chars(text: str) -> bool:
    return any(
        ord(c) < MIN_PRINTABLE_CHAR and c not in {"\n", "\r", "\t"} for c in text
    )


def _validate_user_input(text: str) -> str | None:
    """Validate user input. Returns error message or None if valid."""
    if not text:
        return "Please type your message"
    if len(text) > MAX_MESSAGE_LENGTH:
        return f"Message too long: {len(text)}/{MAX_MESSAGE_LENGTH} chars"
    if "\x00" in text or _has_control_chars(text):
        return "No control characters allowed"
    return None


async def _response_listener(
    channels: Channels, pending: dict[uuid.UUID, asyncio.Future]
) -> None:
    """Filter responses and resolve matching futures."""
    while not channels.shutdown.is_set():
        try:
            response = await asyncio.wait_for(channels.responses.get(), timeout=0.5)
        except asyncio.TimeoutError:
            continue
        if future := pending.pop(response.correlation_id, None):
            future.set_result(response.payload)
        channels.responses.task_done()


async def _send_request(
    text: str,
    user_id: uuid.UUID,
    channels: Channels,
    pending: dict[uuid.UUID, asyncio.Future],
) -> str:
    """Send a request and wait for the matching response."""
    corr_id, future = new_id(), asyncio.get_event_loop().create_future()
    pending[corr_id] = future
    await channels.requests.put(
        ChannelRequest(
            correlation_id=corr_id, user_id=user_id, payload=ClientMessage(data=text)
        )
    )
    return await future


async def _handle_user_input(
    text: str,
    user_id: uuid.UUID,
    channels: Channels,
    pending: dict[uuid.UUID, asyncio.Future],
) -> bool:
    """Handle a single user input. Returns True if should exit."""
    if not text or text == "/help":
        if text == "/help":
            print(HELP_TEXT)
        return False
    if text == "/exit":
        return True

    normalized = unicodedata.normalize("NFKC", text).strip()
    if error := _validate_user_input(normalized):
        logger.info("Rejected user input", extra={"length": len(normalized)})
        print(f"Error: {error}")
    else:
        print(await _send_request(normalized, user_id, channels, pending))
    return False


async def _run_input_loop(
    channels: Channels, user_id: uuid.UUID, pending: dict[uuid.UUID, asyncio.Future]
) -> None:
    """Read input, send requests, await responses."""
    loop = asyncio.get_event_loop()
    while not channels.shutdown.is_set():
        try:
            text = await loop.run_in_executor(None, input, "> ")
        except EOFError:
            break
        if await _handle_user_input(text.strip(), user_id, channels, pending):
            break
    channels.shutdown.set()


async def run_cli_pool(channels: Channels, user_id: uuid.UUID) -> None:
    """Run CLI transport - single worker, handles stdin/stdout."""
    user = get_or_create_user(user_id)
    logger.info("Starting CLI transport", extra={"user_id": str(user.id)})
    print(f"User: {user.id}\nType /help for commands.\n")

    pending: dict[uuid.UUID, asyncio.Future[str]] = {}
    listener = asyncio.create_task(_response_listener(channels, pending))
    try:
        await _run_input_loop(channels, user.id, pending)
    finally:
        listener.cancel()
        await asyncio.gather(listener, return_exceptions=True)
