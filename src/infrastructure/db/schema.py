import asyncio

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
        user_id TEXT NOT NULL
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
        created_ts REAL NOT NULL
    );
    CREATE TABLE IF NOT EXISTS user_knowledge_areas (
        knowledge_id TEXT PRIMARY KEY,
        area_id TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS user_knowledge_areas_area_id_idx
        ON user_knowledge_areas(area_id);
    -- Leaf coverage tracking: status of each leaf area in an interview
    CREATE TABLE IF NOT EXISTS leaf_coverage (
        leaf_id TEXT PRIMARY KEY,
        root_area_id TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        summary_text TEXT,
        vector TEXT,
        updated_at REAL NOT NULL
    );
    CREATE INDEX IF NOT EXISTS leaf_coverage_root_area_idx
        ON leaf_coverage(root_area_id);
    CREATE INDEX IF NOT EXISTS leaf_coverage_status_idx
        ON leaf_coverage(status);

    -- Active interview context: current state per user
    CREATE TABLE IF NOT EXISTS active_interview_context (
        user_id TEXT PRIMARY KEY,
        root_area_id TEXT NOT NULL,
        active_leaf_id TEXT NOT NULL,
        question_text TEXT,
        created_at REAL NOT NULL
    );
"""


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

        await ensure_column_async(
            conn,
            "users",
            "current_area_id",
            "current_area_id TEXT",
        )
        await ensure_column_async(
            conn,
            "life_areas",
            "extracted_at",
            "extracted_at REAL",
        )
        # Migration: drop deprecated tables if they exist
        await conn.execute("DROP TABLE IF EXISTS criteria")
        await conn.execute("DROP TABLE IF EXISTS life_area_messages")
        await conn.execute("DROP TABLE IF EXISTS leaf_extraction_queue")
        await conn.execute("DROP TABLE IF EXISTS area_summaries")

        # Migration: recreate user_knowledge_areas without user_id column
        await conn.execute("DROP TABLE IF EXISTS user_knowledge_areas")
        await conn.executescript("""
            CREATE TABLE IF NOT EXISTS user_knowledge_areas (
                knowledge_id TEXT PRIMARY KEY,
                area_id TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS user_knowledge_areas_area_id_idx
                ON user_knowledge_areas(area_id);
        """)

        await conn.commit()
        _db_initialized_paths.add(db_path)
