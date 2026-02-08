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
    """
    if isinstance(exc, (ConnectionError, TimeoutError)):
        return True
    if isinstance(exc, HTTPStatusError):
        return exc.response.status_code in RETRYABLE_STATUS_CODES
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
    max_attempts: int = 3,
    initial_wait: float = 1.0,
    max_wait: float = 10.0,
) -> T:
    """Invoke an async LLM call with exponential backoff retry.

    Args:
        invoke_fn: Async callable that performs the LLM invocation
        max_attempts: Maximum number of retry attempts (default: 3)
        initial_wait: Initial wait time in seconds (default: 1.0)
        max_wait: Maximum wait time in seconds (default: 10.0)

    Returns:
        The result from the successful invocation

    Raises:
        The last exception if all retries fail
    """

    @retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=initial_wait, max=max_wait),
        retry=retry_if_exception(_is_retryable_exception),
        before_sleep=_log_retry,
        reraise=True,
    )
    async def _invoke_with_retry() -> T:
        return await invoke_fn()

    return await _invoke_with_retry()
