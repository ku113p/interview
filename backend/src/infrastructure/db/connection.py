import asyncio
import fcntl
import logging
import os
import sqlite3
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import TypeVar

import aiosqlite
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")

# SQLite retry configuration
SQLITE_MAX_RETRIES = 5
SQLITE_INITIAL_WAIT = 0.1  # 100ms
SQLITE_MAX_WAIT = 2.0  # 2 seconds

# Process-level lock to serialize write transactions (in-process)
_transaction_lock = asyncio.Lock()


def _release_file_lock(lock_file: object, lock_path: str) -> None:
    """Release file lock, close file, and delete lock file."""
    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
    lock_file.close()
    try:
        os.unlink(lock_path)
    except OSError:
        pass  # File may already be deleted by another process
    logger.debug("Released file lock", extra={"lock_path": lock_path})


@asynccontextmanager
async def _file_lock(lock_path: str) -> AsyncGenerator[None, None]:
    """Cross-process file lock using flock. Waits until lock is available."""
    loop = asyncio.get_event_loop()
    lock_file = open(lock_path, "w")  # noqa: ASYNC230
    try:
        await loop.run_in_executor(None, fcntl.flock, lock_file.fileno(), fcntl.LOCK_EX)
        logger.debug("Acquired file lock", extra={"lock_path": lock_path})
        yield
    finally:
        _release_file_lock(lock_file, lock_path)


def get_db_path() -> str:
    """Get database path from environment or use default."""
    return os.environ.get("INTERVIEW_DB_PATH", "interview.db")


async def _setup_connection(db_path: str) -> aiosqlite.Connection:
    """Create and configure a database connection with WAL mode."""
    from src.infrastructure.db.schema import init_schema_async

    conn = await aiosqlite.connect(db_path, timeout=30.0)
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA journal_mode = WAL")
    await conn.execute("PRAGMA busy_timeout = 30000")
    await conn.execute("PRAGMA foreign_keys = ON")
    await init_schema_async(conn, db_path)
    return conn


async def _close_connection(conn: aiosqlite.Connection | None, db_path: str) -> None:
    """Close connection and log."""
    if conn is not None:
        await conn.close()
        logger.debug("Closed database connection", extra={"db_path": db_path})


def _is_sqlite_busy_error(exc: BaseException) -> bool:
    """Check if exception is a retryable SQLite BUSY/LOCKED error."""
    if not isinstance(exc, sqlite3.OperationalError):
        return False
    msg = str(exc).lower()
    return "locked" in msg or "busy" in msg


def _log_sqlite_retry(retry_state: RetryCallState) -> None:
    """Log SQLite retry attempts for debugging."""
    logger.warning(
        "SQLite retry",
        extra={
            "attempt": retry_state.attempt_number,
            "exception": str(retry_state.outcome.exception()),
        },
    )


async def execute_with_retry(
    fn: Callable[[], Awaitable[T]],
    max_attempts: int = SQLITE_MAX_RETRIES,
    initial_wait: float = SQLITE_INITIAL_WAIT,
    max_wait: float = SQLITE_MAX_WAIT,
) -> T:
    """Execute async SQLite operation with retry on BUSY/LOCKED errors.

    Args:
        fn: Async callable to execute
        max_attempts: Maximum retry attempts (default: 5)
        initial_wait: Initial wait in seconds (default: 0.1)
        max_wait: Maximum wait in seconds (default: 2.0)

    Returns:
        Result from successful execution

    Raises:
        Last exception if all retries fail
    """

    @retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential_jitter(initial=initial_wait, max=max_wait, jitter=0.1),
        retry=retry_if_exception(_is_sqlite_busy_error),
        before_sleep=_log_sqlite_retry,
        reraise=True,
    )
    async def _execute() -> T:
        return await fn()

    return await _execute()


@asynccontextmanager
async def _get_connection_inner(
    db_path: str,
) -> AsyncGenerator[aiosqlite.Connection, None]:
    """Inner connection logic without locking."""
    conn: aiosqlite.Connection | None = None
    try:
        conn = await _setup_connection(db_path)
        logger.debug("Opened database connection", extra={"db_path": db_path})
        yield conn
    except Exception:
        logger.exception("Database connection failed", extra={"db_path": db_path})
        raise
    finally:
        await _close_connection(conn, db_path)


@asynccontextmanager
async def get_connection() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Async context manager for database connections with cross-process locking."""
    db_path = get_db_path()
    lock_path = f"{db_path}.lock"

    async with _file_lock(lock_path):
        async with _get_connection_inner(db_path) as conn:
            yield conn


async def _handle_transaction_error(conn: aiosqlite.Connection, db_path: str) -> None:
    """Attempt rollback on transaction error."""
    try:
        await conn.rollback()
    except Exception:
        logger.exception("Rollback failed", extra={"db_path": db_path})
    logger.exception("Database transaction failed", extra={"db_path": db_path})


@asynccontextmanager
async def _transaction_inner(
    db_path: str,
) -> AsyncGenerator[aiosqlite.Connection, None]:
    """Inner transaction logic - setup, yield, commit/rollback, cleanup."""
    conn: aiosqlite.Connection | None = None
    try:
        conn = await _setup_connection(db_path)
        await conn.execute("BEGIN")
        yield conn
        await execute_with_retry(conn.commit)
    except Exception:
        if conn is not None:
            await _handle_transaction_error(conn, db_path)
        raise
    finally:
        await _close_connection(conn, db_path)


@asynccontextmanager
async def transaction() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Async context manager for database transactions with automatic rollback.

    Uses two-level locking for safety:
    1. File lock (fcntl.flock) - serializes across processes
    2. asyncio.Lock - serializes within same process (faster, no syscall)
    3. Retry on commit - fallback for any edge cases
    """
    db_path = get_db_path()
    lock_path = f"{db_path}.lock"

    async with _file_lock(lock_path):
        async with _transaction_lock:
            async with _transaction_inner(db_path) as conn:
                yield conn
