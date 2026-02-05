import logging
import os
import sqlite3
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger(__name__)


def get_db_path() -> str:
    """Get database path from environment or use default."""
    return os.environ.get("INTERVIEW_DB_PATH", "interview.db")


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:  # noqa: PLR0915
    """Context manager for database connections with proper error handling.

    Yields:
        sqlite3.Connection: Active database connection with row factory configured
    """
    db_path = get_db_path()
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        # Ensure schema is initialized
        from src.infrastructure.db.schema import init_schema

        init_schema(conn, db_path)
    except Exception:
        if conn is not None:
            conn.close()
            conn = None  # Prevent double-close in finally block
        logger.exception("Database connection setup failed", extra={"db_path": db_path})
        raise
    try:
        logger.debug("Opened database connection", extra={"db_path": db_path})
        yield conn
    finally:
        if conn is not None:
            conn.close()
            logger.debug("Closed database connection", extra={"db_path": db_path})


@contextmanager
def transaction() -> Generator[sqlite3.Connection, None, None]:  # noqa: PLR0915
    """Context manager for database transactions with automatic rollback on error.

    Yields:
        sqlite3.Connection: Active connection within a transaction

    Raises:
        Exception: Re-raises any exceptions from the transaction body after rollback
    """
    db_path = get_db_path()
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        from src.infrastructure.db.schema import init_schema

        init_schema(conn, db_path)
    except Exception:
        if conn is not None:
            conn.close()
            conn = None  # Prevent double-close in finally block
        logger.exception(
            "Database transaction setup failed", extra={"db_path": db_path}
        )
        raise
    try:
        conn.execute("BEGIN")
        yield conn
        conn.commit()
    except Exception as original_exc:
        try:
            conn.rollback()
        except Exception:
            logger.exception(
                "Rollback failed (original error will be raised)",
                extra={"db_path": db_path},
            )
        logger.exception("Database transaction failed", extra={"db_path": db_path})
        raise original_exc
    finally:
        if conn is not None:
            conn.close()
            logger.debug("Closed database connection", extra={"db_path": db_path})
