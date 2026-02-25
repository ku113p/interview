"""Telegram transport for handling bot communication."""

import asyncio
import contextlib
import io
import logging
import uuid
from collections.abc import AsyncIterator, Callable, Coroutine
from typing import Any

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ChatAction
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from src.config.telegram_settings import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_MAX_MESSAGE_LENGTH,
    TELEGRAM_MODE,
    TELEGRAM_WEBHOOK_HOST,
    TELEGRAM_WEBHOOK_PATH,
    TELEGRAM_WEBHOOK_SECRET,
    TELEGRAM_WEBHOOK_URL,
    get_webhook_port,
    validate_telegram_config,
)
from src.domain import ClientMessage, MediaMessage, MessageType
from src.processes.auth.interfaces import AuthRequest
from src.processes.interview.interfaces import ChannelRequest, ChannelResponse
from src.runtime import Channels
from src.shared.ids import new_id

logger = logging.getLogger(__name__)


AUTH_TIMEOUT_SECONDS = 30.0
SEND_RETRY_ATTEMPTS = 3
SEND_RETRY_BASE_DELAY = 1.0  # seconds
TYPING_INTERVAL_SECONDS = 4.0


async def _typing_loop(bot: Bot, chat_id: int, stop: asyncio.Event) -> None:
    """Send 'typing' chat action every few seconds until *stop* is set."""
    while not stop.is_set():
        try:
            await bot.send_chat_action(chat_id, ChatAction.TYPING)
        except TelegramNetworkError:
            pass
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(stop.wait(), timeout=TYPING_INTERVAL_SECONDS)


@contextlib.asynccontextmanager
async def _typing(bot: Bot, chat_id: int) -> AsyncIterator[None]:
    """Show 'typing' indicator for the duration of the block."""
    stop = asyncio.Event()
    task = asyncio.create_task(_typing_loop(bot, chat_id, stop))
    try:
        yield
    finally:
        stop.set()
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


async def _retry_send(
    coro_factory: Callable[[], Coroutine[Any, Any, Any]],
    description: str,
) -> None:
    """Retry a send operation with exponential backoff."""
    for attempt in range(SEND_RETRY_ATTEMPTS):
        try:
            await coro_factory()
            return
        except TelegramNetworkError:
            if attempt == SEND_RETRY_ATTEMPTS - 1:
                raise
            delay = SEND_RETRY_BASE_DELAY * (2**attempt)
            logger.warning(
                "Network error %s, retrying in %.1fs (attempt %d/%d)",
                description,
                delay,
                attempt + 1,
                SEND_RETRY_ATTEMPTS,
            )
            await asyncio.sleep(delay)


async def _safe_reply(message: Message, text: str) -> None:
    """Send a reply, logging if network is unavailable."""
    try:
        await message.reply(text)
    except TelegramNetworkError:
        logger.warning("Could not send reply - network unavailable")


async def _get_user_id(
    telegram_id: int,
    display_name: str | None,
    channels: Channels,
) -> uuid.UUID:
    """Send AuthRequest, await user_id via future."""
    future: asyncio.Future[uuid.UUID] = asyncio.get_running_loop().create_future()
    await channels.auth_requests.put(
        AuthRequest(
            provider="telegram",
            external_id=str(telegram_id),
            display_name=display_name,
            response_future=future,
        )
    )
    return await asyncio.wait_for(future, timeout=AUTH_TIMEOUT_SECONDS)


async def _send_request(
    user_id: uuid.UUID,
    client_message: ClientMessage,
    channels: Channels,
    pending_responses: dict[uuid.UUID, asyncio.Future[str]],
) -> str:
    """Send request to graph workers and await response."""
    corr_id = new_id()
    future: asyncio.Future[str] = asyncio.get_running_loop().create_future()
    pending_responses[corr_id] = future
    await channels.requests.put(
        ChannelRequest(
            correlation_id=corr_id,
            user_id=user_id,
            client_message=client_message,
        )
    )
    return await future


def _split_message(text: str, max_length: int) -> list[str]:
    """Split long message into chunks at word boundaries."""
    if len(text) <= max_length:
        return [text]
    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break
        split_at = text.rfind(" ", 0, max_length)
        if split_at == -1:
            split_at = max_length
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()
    return chunks


async def _send_response(bot: Bot, chat_id: int, text: str) -> None:
    """Send response, splitting if too long."""
    for chunk in _split_message(text, TELEGRAM_MAX_MESSAGE_LENGTH):
        await _retry_send(
            lambda c=chunk: bot.send_message(chat_id, c),
            "sending response",
        )


async def _dispatch_responses(
    channels: Channels,
    pending_responses: dict[uuid.UUID, asyncio.Future[str]],
) -> None:
    """Match graph responses to pending futures."""
    while not channels.shutdown.is_set():
        try:
            response: ChannelResponse = await asyncio.wait_for(
                channels.responses.get(), timeout=0.5
            )
        except asyncio.TimeoutError:
            continue
        if future := pending_responses.pop(response.correlation_id, None):
            future.set_result(response.response_text)
        channels.responses.task_done()


def _get_display_name(message: Message) -> str | None:
    """Extract display name from Telegram message."""
    user = message.from_user
    if not user:
        return None
    if user.username:
        return user.username
    if user.first_name:
        return user.first_name
    return None


async def _handle_text_message(
    message: Message,
    bot: Bot,
    channels: Channels,
    pending_responses: dict[uuid.UUID, asyncio.Future[str]],
) -> None:
    """Process text message through graph."""
    if not message.from_user or not message.text:
        return
    try:
        async with _typing(bot, message.chat.id):
            user_id = await _get_user_id(
                message.from_user.id, _get_display_name(message), channels
            )
            client_msg = ClientMessage(data=message.text)
            response = await _send_request(
                user_id, client_msg, channels, pending_responses
            )
            await _send_response(bot, message.chat.id, response)
    except asyncio.TimeoutError:
        await _safe_reply(message, "Service temporarily unavailable. Please try again.")
    except Exception:
        logger.exception("Failed to process text message")
        await _safe_reply(message, "An error occurred. Please try again.")


async def _download_media(file_id: str, bot: Bot) -> io.BytesIO | None:
    """Download media file by ID, return BytesIO or None on failure."""
    file = await bot.get_file(file_id)
    if not file.file_path:
        return None
    data = await bot.download_file(file.file_path)
    return io.BytesIO(data.read()) if data else None


async def _process_voice(
    message: Message,
    bot: Bot,
    channels: Channels,
    pending_responses: dict[uuid.UUID, asyncio.Future[str]],
) -> None:
    """Download, transcribe, and respond to voice message."""
    if not message.voice:
        return
    voice_data = await _download_media(message.voice.file_id, bot)
    if not voice_data:
        await _safe_reply(message, "Failed to download voice message")
        return
    user_id = await _get_user_id(
        message.from_user.id, _get_display_name(message), channels
    )
    media = MediaMessage(type=MessageType.audio, content=voice_data)
    client_msg = ClientMessage(data=media)
    response = await _send_request(user_id, client_msg, channels, pending_responses)
    await _send_response(bot, message.chat.id, response)


async def _handle_voice_message(
    message: Message,
    bot: Bot,
    channels: Channels,
    pending_responses: dict[uuid.UUID, asyncio.Future[str]],
) -> None:
    """Process voice message through graph."""
    if not message.from_user or not message.voice:
        return
    try:
        async with _typing(bot, message.chat.id):
            await _process_voice(message, bot, channels, pending_responses)
    except asyncio.TimeoutError:
        await _safe_reply(message, "Service temporarily unavailable. Please try again.")
    except Exception:
        logger.exception("Failed to process voice message")
        await _safe_reply(message, "An error occurred. Please try again.")


async def _process_video_note(
    message: Message,
    bot: Bot,
    channels: Channels,
    pending_responses: dict[uuid.UUID, asyncio.Future[str]],
) -> None:
    """Download, transcribe, and respond to video note (video circle)."""
    if not message.video_note:
        return
    video_data = await _download_media(message.video_note.file_id, bot)
    if not video_data:
        await _safe_reply(message, "Failed to download video message")
        return
    user_id = await _get_user_id(
        message.from_user.id, _get_display_name(message), channels
    )
    media = MediaMessage(type=MessageType.video, content=video_data)
    client_msg = ClientMessage(data=media)
    response = await _send_request(user_id, client_msg, channels, pending_responses)
    await _send_response(bot, message.chat.id, response)


async def _handle_video_note_message(
    message: Message,
    bot: Bot,
    channels: Channels,
    pending_responses: dict[uuid.UUID, asyncio.Future[str]],
) -> None:
    """Process video note (video circle) message through graph."""
    if not message.from_user or not message.video_note:
        return
    try:
        async with _typing(bot, message.chat.id):
            await _process_video_note(message, bot, channels, pending_responses)
    except asyncio.TimeoutError:
        await _safe_reply(message, "Service temporarily unavailable. Please try again.")
    except Exception:
        logger.exception("Failed to process video note message")
        await _safe_reply(message, "An error occurred. Please try again.")


def _create_router(
    bot: Bot,
    channels: Channels,
    pending_responses: dict[uuid.UUID, asyncio.Future[str]],
) -> Router:
    """Create message router with handlers."""
    router = Router()

    @router.message(Command("start"))
    async def on_start(message: Message) -> None:
        await _safe_reply(
            message,
            "Hello! I'm your interview assistant.\n\n"
            "Send me a text or voice message to start a conversation.",
        )

    @router.message(F.text.startswith("/"), ~Command("start"))
    async def on_command(message: Message) -> None:
        """Route all commands (except /start) through the graph."""
        await _handle_text_message(message, bot, channels, pending_responses)

    @router.message(F.text)
    async def on_text(message: Message) -> None:
        await _handle_text_message(message, bot, channels, pending_responses)

    @router.message(F.voice)
    async def on_voice(message: Message) -> None:
        await _handle_voice_message(message, bot, channels, pending_responses)

    @router.message(F.video_note)
    async def on_video_note(message: Message) -> None:
        await _handle_video_note_message(message, bot, channels, pending_responses)

    return router


def _setup_bot(channels: Channels) -> tuple[Bot, Dispatcher, asyncio.Task]:
    """Initialize bot, dispatcher, and response dispatcher task."""
    validate_telegram_config()
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    pending_responses: dict[uuid.UUID, asyncio.Future[str]] = {}
    router = _create_router(bot, channels, pending_responses)
    dp.include_router(router)
    dispatcher_task = asyncio.create_task(
        _dispatch_responses(channels, pending_responses)
    )
    return bot, dp, dispatcher_task


async def _cleanup_bot(bot: Bot, dispatcher_task: asyncio.Task) -> None:
    """Cancel dispatcher task and close bot session."""
    dispatcher_task.cancel()
    await asyncio.gather(dispatcher_task, return_exceptions=True)
    await bot.session.close()


async def run_telegram_polling(channels: Channels) -> None:
    """Run Telegram bot in polling mode."""
    bot, dp, dispatcher_task = _setup_bot(channels)
    logger.info("Starting Telegram polling")
    try:
        await dp.start_polling(bot, handle_signals=False)
    finally:
        await _cleanup_bot(bot, dispatcher_task)


async def _create_webhook_app(dp: Dispatcher, bot: Bot) -> web.AppRunner:
    """Create and configure webhook application."""
    app = web.Application()
    secret = TELEGRAM_WEBHOOK_SECRET or None
    handler = SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=secret)
    handler.register(app, path=TELEGRAM_WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    await bot.set_webhook(url=TELEGRAM_WEBHOOK_URL, secret_token=secret)
    runner = web.AppRunner(app)
    await runner.setup()
    return runner


async def _run_webhook_server(runner: web.AppRunner, channels: Channels) -> None:
    """Start webhook server and wait for shutdown."""
    site = web.TCPSite(runner, TELEGRAM_WEBHOOK_HOST, get_webhook_port())
    await site.start()
    while not channels.shutdown.is_set():
        await asyncio.sleep(0.5)


async def run_telegram_webhook(channels: Channels) -> None:
    """Run Telegram bot in webhook mode."""
    bot, dp, dispatcher_task = _setup_bot(channels)
    logger.info("Starting Telegram webhook", extra={"url": TELEGRAM_WEBHOOK_URL})
    runner = await _create_webhook_app(dp, bot)
    try:
        await _run_webhook_server(runner, channels)
    finally:
        await bot.delete_webhook()
        await runner.cleanup()
        await _cleanup_bot(bot, dispatcher_task)


async def run_telegram(channels: Channels) -> None:
    """Run Telegram transport in configured mode."""
    if TELEGRAM_MODE == "webhook":
        await run_telegram_webhook(channels)
    else:
        await run_telegram_polling(channels)
