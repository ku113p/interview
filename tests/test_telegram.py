"""Tests for Telegram transport utilities."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.exceptions import TelegramNetworkError
from src.processes.transport.telegram import (
    SEND_RETRY_ATTEMPTS,
    _retry_send,
    _safe_reply,
    _split_message,
)


def _make_network_error(msg: str = "network error") -> TelegramNetworkError:
    """Create a TelegramNetworkError with mock method."""
    return TelegramNetworkError(method=MagicMock(), message=msg)


class TestRetrySend:
    """Tests for _retry_send function."""

    @pytest.mark.asyncio
    async def test_succeeds_on_first_attempt(self):
        """Should return immediately when coro succeeds."""
        coro_factory = AsyncMock()

        await _retry_send(coro_factory, "test operation")

        assert coro_factory.call_count == 1

    @pytest.mark.asyncio
    async def test_retries_on_network_error(self):
        """Should retry when TelegramNetworkError occurs."""
        coro_factory = AsyncMock(side_effect=[_make_network_error(), None])

        with patch("src.processes.transport.telegram.asyncio.sleep"):
            await _retry_send(coro_factory, "test operation")

        assert coro_factory.call_count == 2

    @pytest.mark.asyncio
    async def test_raises_after_max_retries(self):
        """Should raise TelegramNetworkError after max attempts."""
        coro_factory = AsyncMock(side_effect=_make_network_error())

        with patch("src.processes.transport.telegram.asyncio.sleep"):
            with pytest.raises(TelegramNetworkError):
                await _retry_send(coro_factory, "test operation")

        assert coro_factory.call_count == SEND_RETRY_ATTEMPTS

    @pytest.mark.asyncio
    async def test_exponential_backoff_delays(self):
        """Should use exponential backoff between retries."""
        coro_factory = AsyncMock(
            side_effect=[
                _make_network_error(),
                _make_network_error(),
                None,
            ]
        )
        sleep_mock = AsyncMock()

        with patch("src.processes.transport.telegram.asyncio.sleep", sleep_mock):
            await _retry_send(coro_factory, "test operation")

        # Check delays: 1.0 * 2^0 = 1.0, 1.0 * 2^1 = 2.0
        assert sleep_mock.call_count == 2
        sleep_mock.assert_any_call(1.0)
        sleep_mock.assert_any_call(2.0)


class TestSafeReply:
    """Tests for _safe_reply function."""

    @pytest.mark.asyncio
    async def test_sends_reply_successfully(self):
        """Should call message.reply with text."""
        message = AsyncMock()

        await _safe_reply(message, "test message")

        message.reply.assert_called_once_with("test message")

    @pytest.mark.asyncio
    async def test_logs_warning_on_network_error(self):
        """Should log warning when network is unavailable."""
        message = AsyncMock()
        message.reply.side_effect = _make_network_error()

        with patch("src.processes.transport.telegram.logger") as mock_logger:
            await _safe_reply(message, "test message")

        mock_logger.warning.assert_called_once()


class TestSplitMessage:
    """Tests for _split_message function."""

    def test_short_message_unchanged(self):
        """Should return single chunk for short messages."""
        result = _split_message("Hello", 100)

        assert result == ["Hello"]

    def test_splits_at_word_boundary(self):
        """Should split at word boundaries when possible."""
        result = _split_message("Hello World Test", 12)

        assert result == ["Hello World", "Test"]

    def test_splits_long_word(self):
        """Should split within word if no space found."""
        result = _split_message("abcdefghij", 5)

        assert result == ["abcde", "fghij"]

    def test_exact_length_no_split(self):
        """Should not split if exactly at max length."""
        result = _split_message("Hello", 5)

        assert result == ["Hello"]
