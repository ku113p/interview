"""Tests for the schema migration runner."""

from unittest.mock import AsyncMock, patch

import aiosqlite
import pytest
from src.infrastructure.db.schema import (
    _MIGRATIONS,
    _db_initialized_paths,
    init_schema_async,
)


async def _open_conn(db_path: str) -> aiosqlite.Connection:
    conn = await aiosqlite.connect(db_path)
    conn.row_factory = aiosqlite.Row
    return conn


async def _get_versions(conn: aiosqlite.Connection) -> list[int]:
    cursor = await conn.execute("SELECT version FROM schema_version ORDER BY version")
    rows = await cursor.fetchall()
    return [row["version"] for row in rows]


async def _seed_version_row(db_path: str) -> None:
    """Create schema_version table and pre-insert version 1."""
    conn = await _open_conn(db_path)
    try:
        await conn.executescript(
            "CREATE TABLE IF NOT EXISTS schema_version"
            " (version INTEGER PRIMARY KEY,"
            " description TEXT NOT NULL,"
            " applied_at REAL NOT NULL);"
        )
        await conn.execute(
            "INSERT INTO schema_version (version, description, applied_at)"
            " VALUES (1, 'pre-inserted', 0.0)"
        )
        await conn.commit()
    finally:
        await conn.close()


@pytest.fixture
def fresh_db(tmp_path):
    """Yield a path to a fresh SQLite database file."""
    db_path = str(tmp_path / "test.db")
    _db_initialized_paths.discard(db_path)
    yield db_path
    _db_initialized_paths.discard(db_path)


class TestMigrationRunner:
    """Test the schema migration runner."""

    async def test_fresh_db_records_all_migrations(self, fresh_db):
        """Fresh DB should have all migration versions recorded."""
        conn = await _open_conn(fresh_db)
        try:
            await init_schema_async(conn, fresh_db)
            versions = await _get_versions(conn)
            assert versions == [m.version for m in _MIGRATIONS]
        finally:
            await conn.close()

    async def test_migrations_are_idempotent(self, fresh_db):
        """Re-initializing should not duplicate migration rows."""
        conn = await _open_conn(fresh_db)
        try:
            await init_schema_async(conn, fresh_db)
        finally:
            await conn.close()

        _db_initialized_paths.discard(fresh_db)

        conn = await _open_conn(fresh_db)
        try:
            await init_schema_async(conn, fresh_db)
            cursor = await conn.execute("SELECT count(*) as cnt FROM schema_version")
            row = await cursor.fetchone()
            assert row["cnt"] == len(_MIGRATIONS)
        finally:
            await conn.close()

    async def test_skips_already_applied(self, fresh_db):
        """Pre-inserted version rows should not trigger their migration again."""
        await _seed_version_row(fresh_db)

        spy = AsyncMock(wraps=_MIGRATIONS[0].migrate)
        patched = _MIGRATIONS.copy()
        patched[0] = patched[0]._replace(migrate=spy)

        conn = await _open_conn(fresh_db)
        try:
            with patch("src.infrastructure.db.schema._MIGRATIONS", patched):
                await init_schema_async(conn, fresh_db)
            spy.assert_not_called()
            versions = await _get_versions(conn)
            assert versions == [m.version for m in _MIGRATIONS]
        finally:
            await conn.close()

    async def test_partial_failure_preserves_earlier_migrations(self, fresh_db):
        """If migration N fails, migrations 1..N-1 should be durably recorded."""
        failing = AsyncMock(side_effect=RuntimeError("boom"))
        patched = _MIGRATIONS.copy()
        patched[2] = patched[2]._replace(migrate=failing)

        conn = await _open_conn(fresh_db)
        try:
            with pytest.raises(RuntimeError, match="boom"):
                with patch("src.infrastructure.db.schema._MIGRATIONS", patched):
                    await init_schema_async(conn, fresh_db)
        finally:
            await conn.close()

        # Fresh connection to verify only committed state on disk
        conn = await _open_conn(fresh_db)
        try:
            versions = await _get_versions(conn)
            assert versions == [1, 2]
        finally:
            await conn.close()
