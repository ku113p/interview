import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import NamedTuple

import aiosqlite

# Track which database file has been initialized to avoid redundant initialization
_db_initialized_paths: set[str] = set()
_init_lock = asyncio.Lock()

_SCHEMA_SQL = """
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        mode TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS histories (
        id TEXT PRIMARY KEY,
        message_data TEXT NOT NULL,
        user_id TEXT NOT NULL,
        created_ts REAL NOT NULL
    );
    CREATE TABLE IF NOT EXISTS life_areas (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        parent_id TEXT,
        user_id TEXT NOT NULL,
        covered_at REAL
    );
    -- Leaf-to-history join table: links leaves to their conversation messages
    CREATE TABLE IF NOT EXISTS leaf_history (
        leaf_id TEXT NOT NULL,
        history_id TEXT NOT NULL,
        PRIMARY KEY (leaf_id, history_id)
    );
    CREATE INDEX IF NOT EXISTS leaf_history_leaf_idx ON leaf_history(leaf_id);
    CREATE INDEX IF NOT EXISTS histories_user_id_idx
        ON histories(user_id);
    CREATE INDEX IF NOT EXISTS histories_created_ts_idx
        ON histories(created_ts);
    CREATE INDEX IF NOT EXISTS life_areas_user_id_idx
        ON life_areas(user_id);
    CREATE INDEX IF NOT EXISTS life_areas_parent_id_idx
        ON life_areas(parent_id);
    CREATE TABLE IF NOT EXISTS user_knowledge (
        id TEXT PRIMARY KEY,
        description TEXT NOT NULL,
        kind TEXT NOT NULL,
        confidence REAL NOT NULL,
        created_ts REAL NOT NULL,
        summary_id TEXT
    );
    -- Per-turn summaries for each leaf area interview
    CREATE TABLE IF NOT EXISTS summaries (
        id TEXT PRIMARY KEY,
        area_id TEXT NOT NULL,
        summary_text TEXT NOT NULL,
        question_id TEXT,
        answer_id TEXT,
        vector TEXT,
        created_at REAL NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_summaries_area_id ON summaries(area_id);
"""

_SCHEMA_VERSION_DDL = (
    "CREATE TABLE IF NOT EXISTS schema_version"
    " (version INTEGER PRIMARY KEY, description TEXT NOT NULL, applied_at REAL NOT NULL)"
)


class Migration(NamedTuple):
    version: int
    description: str
    migrate: Callable[[aiosqlite.Connection], Awaitable[None]]


async def ensure_column_async(
    conn: aiosqlite.Connection, table: str, column: str, definition: str
) -> None:
    """Add a column to a table if it doesn't already exist (migration helper).

    Args:
        conn: Active database connection
        table: Table name
        column: Column name to add
        definition: Full column definition (e.g., "created_ts REAL NOT NULL DEFAULT 0")
    """
    cursor = await conn.execute(f"PRAGMA table_info({table})")
    rows = await cursor.fetchall()
    columns = {row["name"] for row in rows}
    if column in columns:
        return
    await conn.execute(f"ALTER TABLE {table} ADD COLUMN {definition}")


async def _drop_column_if_exists(
    conn: aiosqlite.Connection, table: str, column: str
) -> None:
    """Drop a column from a table if it exists (migration helper, SQLite 3.35+)."""
    cursor = await conn.execute(f"PRAGMA table_info({table})")
    rows = await cursor.fetchall()
    columns = {row["name"] for row in rows}
    if column not in columns:
        return
    await conn.execute(f"ALTER TABLE {table} DROP COLUMN {column}")


# --- Individual migrations ---


async def _migration_001(conn: aiosqlite.Connection) -> None:
    await ensure_column_async(conn, "users", "current_area_id", "current_area_id TEXT")


async def _migration_002(conn: aiosqlite.Connection) -> None:
    await ensure_column_async(conn, "life_areas", "covered_at", "covered_at REAL")


async def _migration_003(conn: aiosqlite.Connection) -> None:
    await ensure_column_async(conn, "user_knowledge", "summary_id", "summary_id TEXT")
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_user_knowledge_summary_id"
        " ON user_knowledge(summary_id)"
    )


async def _migration_004(conn: aiosqlite.Connection) -> None:
    await _drop_column_if_exists(conn, "life_areas", "extracted_at")


async def _migration_005(conn: aiosqlite.Connection) -> None:
    for table in (
        "criteria",
        "life_area_messages",
        "leaf_extraction_queue",
        "area_summaries",
        "leaf_coverage",
        "active_interview_context",
        "user_knowledge_areas",
    ):
        await conn.execute(f"DROP TABLE IF EXISTS {table}")


async def _migration_006(conn: aiosqlite.Connection) -> None:
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id TEXT PRIMARY KEY,
            key_hash TEXT NOT NULL UNIQUE,
            key_prefix TEXT NOT NULL,
            user_id TEXT NOT NULL,
            label TEXT NOT NULL,
            created_at REAL NOT NULL
        )
    """)
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id)"
    )


_MIGRATIONS: list[Migration] = [
    Migration(1, "Add current_area_id to users", _migration_001),
    Migration(2, "Add covered_at to life_areas", _migration_002),
    Migration(3, "Add summary_id + index to user_knowledge", _migration_003),
    Migration(4, "Drop extracted_at from life_areas", _migration_004),
    Migration(5, "Drop deprecated tables", _migration_005),
    Migration(6, "Create api_keys table", _migration_006),
]


# --- Migration runner ---


async def _get_applied_versions(conn: aiosqlite.Connection) -> set[int]:
    cursor = await conn.execute("SELECT version FROM schema_version")
    rows = await cursor.fetchall()
    return {row["version"] for row in rows}


async def _record_migration(conn: aiosqlite.Connection, migration: Migration) -> None:
    await conn.execute(
        "INSERT OR IGNORE INTO schema_version (version, description, applied_at)"
        " VALUES (?, ?, ?)",
        (migration.version, migration.description, time.time()),
    )


async def _apply_migrations(conn: aiosqlite.Connection) -> None:
    applied = await _get_applied_versions(conn)
    for migration in _MIGRATIONS:
        if migration.version in applied:
            continue
        await migration.migrate(conn)
        await _record_migration(conn, migration)
        await conn.commit()


async def init_schema_async(conn: aiosqlite.Connection, db_path: str) -> None:
    """Initialize database schema if not already done for this path.

    Async-safe: uses an asyncio lock to prevent concurrent initialization.

    Args:
        conn: Active database connection
        db_path: Path to the database file
    """
    # Fast path: check without lock if already initialized
    if db_path in _db_initialized_paths:
        return

    async with _init_lock:
        # Double-check after acquiring lock
        if db_path in _db_initialized_paths:
            return

        await conn.executescript(_SCHEMA_SQL)
        await conn.execute(_SCHEMA_VERSION_DDL)
        await conn.commit()
        await _apply_migrations(conn)
        _db_initialized_paths.add(db_path)
