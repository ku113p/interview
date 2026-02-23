"""Retry utilities for LLM API calls with exponential backoff."""

import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

from httpx import HTTPStatusError
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from src.config.settings import (
    RETRY_INITIAL_WAIT,
    RETRY_MAX_ATTEMPTS,
    RETRY_MAX_WAIT,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")

# HTTP status codes that are safe to retry (transient errors)
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def _is_retryable_exception(exc: BaseException) -> bool:
    """Check if an exception is retryable.

    Retries on:
    - ConnectionError: Network connectivity issues
    - TimeoutError: Request timeouts
    - HTTPStatusError: Only for specific status codes (429, 5xx server errors)
    - ValueError: Structured output parsing failures from OpenAI when reasoning
      models exhaust max_completion_tokens before producing valid JSON. The check
      matches "Structured Output response" substring which is specific to OpenAI's
      error message format (e.g., "Structured Output response did not match...").
    """
    if isinstance(exc, (ConnectionError, TimeoutError)):
        return True
    if isinstance(exc, HTTPStatusError):
        return exc.response.status_code in RETRYABLE_STATUS_CODES
    if isinstance(exc, ValueError) and "Structured Output response" in str(exc):
        return True
    return False


def _log_retry(retry_state: RetryCallState) -> None:
    """Log retry attempts for debugging."""
    logger.warning(
        "LLM call retry",
        extra={
            "attempt": retry_state.attempt_number,
            "exception": str(retry_state.outcome.exception()),
        },
    )


async def invoke_with_retry(
    invoke_fn: Callable[[], Awaitable[T]],
    max_attempts: int = RETRY_MAX_ATTEMPTS,
    initial_wait: float = RETRY_INITIAL_WAIT,
    max_wait: float = RETRY_MAX_WAIT,
) -> T:
    """Invoke an async LLM call with exponential backoff retry.

    Args:
        invoke_fn: Async callable that performs the LLM invocation
        max_attempts: Maximum number of retry attempts (default: RETRY_MAX_ATTEMPTS)
        initial_wait: Initial wait time in seconds, also used as exponential backoff
            multiplier (default: RETRY_INITIAL_WAIT)
        max_wait: Maximum wait time in seconds (default: RETRY_MAX_WAIT)

    Returns:
        The result from the successful invocation

    Raises:
        The last exception if all retries fail

    Note:
        Default values are defined in src.config.settings and can be overridden
        via environment variables (RETRY_MAX_ATTEMPTS, RETRY_INITIAL_WAIT, RETRY_MAX_WAIT).
    """

    @retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=initial_wait, min=initial_wait, max=max_wait),
        retry=retry_if_exception(_is_retryable_exception),
        before_sleep=_log_retry,
        reraise=True,
    )
    async def _invoke_with_retry() -> T:
        return await invoke_fn()

    return await _invoke_with_retry()
