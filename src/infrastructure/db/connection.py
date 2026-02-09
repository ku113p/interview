import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aiosqlite

logger = logging.getLogger(__name__)


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


@asynccontextmanager
async def get_connection() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Async context manager for database connections with proper error handling."""
    db_path = get_db_path()
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


async def _handle_transaction_error(conn: aiosqlite.Connection, db_path: str) -> None:
    """Attempt rollback on transaction error."""
    try:
        await conn.rollback()
    except Exception:
        logger.exception("Rollback failed", extra={"db_path": db_path})
    logger.exception("Database transaction failed", extra={"db_path": db_path})


@asynccontextmanager
async def transaction() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Async context manager for database transactions with automatic rollback."""
    db_path = get_db_path()
    conn: aiosqlite.Connection | None = None
    try:
        conn = await _setup_connection(db_path)
        await conn.execute("BEGIN")
        yield conn
        await conn.commit()
    except Exception:
        if conn is not None:
            await _handle_transaction_error(conn, db_path)
        raise
    finally:
        await _close_connection(conn, db_path)
