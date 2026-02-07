import sqlite3
import threading

# Track which database file has been initialized to avoid redundant initialization
_db_initialized_paths: set[str] = set()
_init_lock = threading.Lock()


def init_schema(conn: sqlite3.Connection, db_path: str) -> None:
    """Initialize database schema if not already done for this path.

    Thread-safe: uses a lock to prevent concurrent initialization of the same database.

    Args:
        conn: Active database connection
        db_path: Path to the database file
    """
    # Fast path: check without lock if already initialized
    if db_path in _db_initialized_paths:
        return

    with _init_lock:
        # Double-check after acquiring lock
        if db_path in _db_initialized_paths:
            return

        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                mode TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS histories (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                user_id TEXT NOT NULL,
                created_ts REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS life_areas (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                parent_id TEXT,
                user_id TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS criteria (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                area_id TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS life_area_messages (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                area_id TEXT NOT NULL,
                created_ts REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS histories_user_id_idx
                ON histories(user_id);
            CREATE INDEX IF NOT EXISTS histories_created_ts_idx
                ON histories(created_ts);
            CREATE INDEX IF NOT EXISTS life_areas_user_id_idx
                ON life_areas(user_id);
            CREATE INDEX IF NOT EXISTS criteria_area_id_idx
                ON criteria(area_id);
            CREATE INDEX IF NOT EXISTS life_area_messages_area_id_idx
                ON life_area_messages(area_id);
            CREATE INDEX IF NOT EXISTS life_area_messages_created_ts_idx
                ON life_area_messages(created_ts);
            CREATE TABLE IF NOT EXISTS area_summaries (
                id TEXT PRIMARY KEY,
                area_id TEXT NOT NULL,
                content TEXT NOT NULL,
                vector BLOB NOT NULL,
                created_ts REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS area_summaries_area_id_idx
                ON area_summaries(area_id);
            CREATE TABLE IF NOT EXISTS user_knowledge (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                kind TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_ts REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS user_knowledge_areas (
                user_id TEXT NOT NULL,
                knowledge_id TEXT NOT NULL,
                area_id TEXT NOT NULL,
                PRIMARY KEY (user_id, knowledge_id)
            );
            CREATE INDEX IF NOT EXISTS user_knowledge_areas_user_id_idx
                ON user_knowledge_areas(user_id);
            CREATE INDEX IF NOT EXISTS user_knowledge_areas_area_id_idx
                ON user_knowledge_areas(area_id);
            """
        )

        ensure_column(
            conn,
            "life_area_messages",
            "created_ts",
            "created_ts REAL NOT NULL DEFAULT 0",
        )
        ensure_column(
            conn,
            "users",
            "current_area_id",
            "current_area_id TEXT",
        )
        conn.commit()
        _db_initialized_paths.add(db_path)


def ensure_column(
    conn: sqlite3.Connection, table: str, column: str, definition: str
) -> None:
    """Add a column to a table if it doesn't already exist (migration helper).

    Args:
        conn: Active database connection
        table: Table name
        column: Column name to add
        definition: Full column definition (e.g., "created_ts REAL NOT NULL DEFAULT 0")
    """
    columns = {
        row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
    }
    if column in columns:
        return
    conn.execute(f"ALTER TABLE {table} ADD COLUMN {definition}")
