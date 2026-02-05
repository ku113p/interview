import sqlite3

# Track which database file has been initialized to avoid redundant initialization
_db_initialized_path: str | None = None


def init_schema(conn: sqlite3.Connection, db_path: str) -> None:
    """Initialize database schema if not already done for this path.

    Args:
        conn: Active database connection
        db_path: Path to the database file
    """
    global _db_initialized_path

    if _db_initialized_path == db_path:
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
        """
    )

    ensure_column(
        conn,
        "life_area_messages",
        "created_ts",
        "created_ts REAL NOT NULL DEFAULT 0",
    )
    conn.commit()
    _db_initialized_path = db_path


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
