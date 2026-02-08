"""Tests for retry utilities."""

import pytest
from httpx import HTTPStatusError, Request, Response
from src.shared.retry import (
    RETRYABLE_STATUS_CODES,
    _is_retryable_exception,
    invoke_with_retry,
)


class TestRetryableStatusCodes:
    """Tests for RETRYABLE_STATUS_CODES configuration."""

    def test_includes_rate_limit(self):
        assert 429 in RETRYABLE_STATUS_CODES

    def test_includes_server_errors(self):
        assert 500 in RETRYABLE_STATUS_CODES
        assert 502 in RETRYABLE_STATUS_CODES
        assert 503 in RETRYABLE_STATUS_CODES
        assert 504 in RETRYABLE_STATUS_CODES

    def test_excludes_client_errors(self):
        assert 400 not in RETRYABLE_STATUS_CODES
        assert 401 not in RETRYABLE_STATUS_CODES
        assert 403 not in RETRYABLE_STATUS_CODES
        assert 404 not in RETRYABLE_STATUS_CODES


class TestIsRetryableException:
    """Tests for _is_retryable_exception function."""

    def test_connection_error_is_retryable(self):
        assert _is_retryable_exception(ConnectionError("failed"))

    def test_timeout_error_is_retryable(self):
        assert _is_retryable_exception(TimeoutError("timed out"))

    def test_rate_limit_is_retryable(self):
        request = Request("POST", "https://api.example.com")
        response = Response(429, request=request)
        exc = HTTPStatusError("Rate limited", request=request, response=response)
        assert _is_retryable_exception(exc)

    def test_server_error_is_retryable(self):
        request = Request("POST", "https://api.example.com")
        for status in [500, 502, 503, 504]:
            response = Response(status, request=request)
            exc = HTTPStatusError("Server error", request=request, response=response)
            assert _is_retryable_exception(exc)

    def test_bad_request_not_retryable(self):
        request = Request("POST", "https://api.example.com")
        response = Response(400, request=request)
        exc = HTTPStatusError("Bad request", request=request, response=response)
        assert not _is_retryable_exception(exc)

    def test_unauthorized_not_retryable(self):
        request = Request("POST", "https://api.example.com")
        response = Response(401, request=request)
        exc = HTTPStatusError("Unauthorized", request=request, response=response)
        assert not _is_retryable_exception(exc)

    def test_value_error_not_retryable(self):
        assert not _is_retryable_exception(ValueError("not retryable"))


class TestInvokeWithRetry:
    """Tests for invoke_with_retry function."""

    @pytest.mark.asyncio
    async def test_returns_result_on_success(self):
        async def success_fn():
            return "success"

        result = await invoke_with_retry(success_fn)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_retries_on_connection_error(self):
        call_count = 0

        async def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Connection failed")
            return "recovered"

        result = await invoke_with_retry(
            failing_then_success, max_attempts=3, initial_wait=0.01
        )
        assert result == "recovered"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retries_on_timeout_error(self):
        call_count = 0

        async def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise TimeoutError("Timeout")
            return "recovered"

        result = await invoke_with_retry(
            failing_then_success, max_attempts=3, initial_wait=0.01
        )
        assert result == "recovered"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retries_on_rate_limit(self):
        call_count = 0

        async def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                request = Request("POST", "https://api.example.com")
                response = Response(429, request=request)
                raise HTTPStatusError(
                    "Rate limited", request=request, response=response
                )
            return "recovered"

        result = await invoke_with_retry(
            failing_then_success, max_attempts=3, initial_wait=0.01
        )
        assert result == "recovered"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_raises_after_max_attempts(self):
        call_count = 0

        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Persistent failure")

        with pytest.raises(ConnectionError, match="Persistent failure"):
            await invoke_with_retry(always_fails, max_attempts=3, initial_wait=0.01)

        assert call_count == 3

    @pytest.mark.asyncio
    async def test_does_not_retry_non_retryable_exception(self):
        call_count = 0

        async def raises_value_error():
            nonlocal call_count
            call_count += 1
            raise ValueError("Not retryable")

        with pytest.raises(ValueError, match="Not retryable"):
            await invoke_with_retry(
                raises_value_error, max_attempts=3, initial_wait=0.01
            )

        assert call_count == 1  # No retries for ValueError

    @pytest.mark.asyncio
    async def test_does_not_retry_bad_request(self):
        call_count = 0

        async def raises_bad_request():
            nonlocal call_count
            call_count += 1
            request = Request("POST", "https://api.example.com")
            response = Response(400, request=request)
            raise HTTPStatusError("Bad request", request=request, response=response)

        with pytest.raises(HTTPStatusError):
            await invoke_with_retry(
                raises_bad_request, max_attempts=3, initial_wait=0.01
            )

        assert call_count == 1  # No retries for 400 errors
