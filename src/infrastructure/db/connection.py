import logging
import os
import sqlite3
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger(__name__)


def get_db_path() -> str:
    """Get database path from environment or use default."""
    return os.environ.get("INTERVIEW_DB_PATH", "interview.db")


def _setup_connection(db_path: str) -> sqlite3.Connection:
    """Create and configure a database connection."""
    from src.infrastructure.db.schema import init_schema

    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    init_schema(conn, db_path)
    return conn


def _close_connection(conn: sqlite3.Connection | None, db_path: str) -> None:
    """Close connection and log."""
    if conn is not None:
        conn.close()
        logger.debug("Closed database connection", extra={"db_path": db_path})


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections with proper error handling."""
    db_path = get_db_path()
    conn: sqlite3.Connection | None = None
    try:
        conn = _setup_connection(db_path)
        logger.debug("Opened database connection", extra={"db_path": db_path})
        yield conn
    except Exception:
        logger.exception("Database connection failed", extra={"db_path": db_path})
        raise
    finally:
        _close_connection(conn, db_path)


def _handle_transaction_error(conn: sqlite3.Connection, db_path: str) -> None:
    """Attempt rollback on transaction error."""
    try:
        conn.rollback()
    except Exception:
        logger.exception("Rollback failed", extra={"db_path": db_path})
    logger.exception("Database transaction failed", extra={"db_path": db_path})


@contextmanager
def transaction() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database transactions with automatic rollback on error."""
    db_path = get_db_path()
    conn: sqlite3.Connection | None = None
    try:
        conn = _setup_connection(db_path)
        conn.execute("BEGIN")
        yield conn
        conn.commit()
    except Exception:
        if conn is not None:
            _handle_transaction_error(conn, db_path)
        raise
    finally:
        _close_connection(conn, db_path)
