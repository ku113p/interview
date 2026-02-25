"""Unit tests for database connection and transaction handling."""

import sqlite3
from unittest.mock import AsyncMock

import pytest
from src.infrastructure.db import managers as db
from src.infrastructure.db.connection import (
    _is_sqlite_busy_error,
    execute_with_retry,
    get_connection,
    transaction,
)
from src.shared.ids import new_id


class TestTransaction:
    """Test the transaction context manager."""

    async def test_transaction_commits_on_success(self, temp_db):
        """Transaction should commit changes when no exception occurs."""
        user_id = new_id()
        user = db.User(id=user_id, name="test", mode="auto", current_area_id=None)

        async with transaction() as conn:
            await db.UsersManager.create(user_id, user, conn=conn, auto_commit=False)

        # Verify data was committed
        result = await db.UsersManager.get_by_id(user_id)
        assert result is not None
        assert result.name == "test"

    async def test_transaction_rolls_back_on_exception(self, temp_db):
        """Transaction should rollback changes when an exception occurs."""
        user_id = new_id()
        user = db.User(
            id=user_id, name="rollback_test", mode="auto", current_area_id=None
        )

        with pytest.raises(ValueError, match="Intentional error"):
            async with transaction() as conn:
                await db.UsersManager.create(
                    user_id, user, conn=conn, auto_commit=False
                )
                # Verify data exists within transaction
                check = await db.UsersManager.get_by_id(user_id, conn=conn)
                assert check is not None
                # Raise exception to trigger rollback
                raise ValueError("Intentional error")

        # Verify data was rolled back
        result = await db.UsersManager.get_by_id(user_id)
        assert result is None

    async def test_transaction_multiple_operations_rollback(self, temp_db):
        """Multiple operations should all rollback on exception."""
        user_id = new_id()
        area_id = new_id()

        user = db.User(id=user_id, name="multi_test", mode="auto", current_area_id=None)
        area = db.LifeArea(
            id=area_id, title="Test Area", parent_id=None, user_id=user_id
        )

        with pytest.raises(RuntimeError):
            async with transaction() as conn:
                await db.UsersManager.create(
                    user_id, user, conn=conn, auto_commit=False
                )
                await db.LifeAreasManager.create(
                    area_id, area, conn=conn, auto_commit=False
                )
                raise RuntimeError("Rollback all")

        # Verify both were rolled back
        assert await db.UsersManager.get_by_id(user_id) is None
        assert await db.LifeAreasManager.get_by_id(area_id) is None


class TestGetConnection:
    """Test the get_connection context manager."""

    async def test_connection_auto_commits_without_conn_param(self, temp_db):
        """Manager should auto-commit when no connection is provided."""
        user_id = new_id()
        user = db.User(
            id=user_id, name="auto_commit", mode="auto", current_area_id=None
        )

        # When conn=None (default), manager creates its own connection and auto-commits
        await db.UsersManager.create(user_id, user)

        # Verify data persisted
        result = await db.UsersManager.get_by_id(user_id)
        assert result is not None

    async def test_connection_requires_explicit_commit(self, temp_db):
        """When conn is provided, caller must commit explicitly."""
        user_id = new_id()
        user = db.User(
            id=user_id, name="explicit_commit", mode="auto", current_area_id=None
        )

        async with get_connection() as conn:
            await db.UsersManager.create(user_id, user, conn=conn, auto_commit=False)
            # Data visible within same connection
            result_in_tx = await db.UsersManager.get_by_id(user_id, conn=conn)
            assert result_in_tx is not None
            await conn.commit()

        # Verify data persisted after explicit commit
        result = await db.UsersManager.get_by_id(user_id)
        assert result is not None

    async def test_wal_mode_enabled(self, temp_db):
        """WAL journal mode should be enabled."""
        async with get_connection() as conn:
            cursor = await conn.execute("PRAGMA journal_mode")
            row = await cursor.fetchone()
            assert row[0].lower() == "wal"

    async def test_busy_timeout_set(self, temp_db):
        """Busy timeout should be set to 30 seconds."""
        async with get_connection() as conn:
            cursor = await conn.execute("PRAGMA busy_timeout")
            row = await cursor.fetchone()
            assert row[0] == 30000


class TestIsSqliteBusyError:
    """Test the _is_sqlite_busy_error helper function."""

    def test_returns_true_for_locked_error(self):
        """Should return True for 'database is locked' error."""
        exc = sqlite3.OperationalError("database is locked")
        assert _is_sqlite_busy_error(exc) is True

    def test_returns_true_for_busy_error(self):
        """Should return True for 'database is busy' error."""
        exc = sqlite3.OperationalError("database is busy")
        assert _is_sqlite_busy_error(exc) is True

    def test_returns_true_case_insensitive(self):
        """Should match regardless of case."""
        exc = sqlite3.OperationalError("DATABASE IS LOCKED")
        assert _is_sqlite_busy_error(exc) is True

    def test_returns_false_for_other_operational_error(self):
        """Should return False for non-busy/locked OperationalError."""
        exc = sqlite3.OperationalError("no such table: foo")
        assert _is_sqlite_busy_error(exc) is False

    def test_returns_false_for_non_operational_error(self):
        """Should return False for other exception types."""
        assert _is_sqlite_busy_error(ValueError("database is locked")) is False
        assert _is_sqlite_busy_error(RuntimeError("busy")) is False


class TestExecuteWithRetry:
    """Test the execute_with_retry function."""

    async def test_returns_result_on_success(self):
        """Should return result when function succeeds."""
        mock_fn = AsyncMock(return_value="success")
        result = await execute_with_retry(mock_fn)
        assert result == "success"
        mock_fn.assert_called_once()

    async def test_retries_on_busy_error(self):
        """Should retry on BUSY error and succeed on subsequent attempt."""
        mock_fn = AsyncMock(
            side_effect=[
                sqlite3.OperationalError("database is locked"),
                "success",
            ]
        )
        result = await execute_with_retry(mock_fn, initial_wait=0.01, max_wait=0.02)
        assert result == "success"
        assert mock_fn.call_count == 2

    async def test_retries_multiple_times(self):
        """Should retry multiple times before succeeding."""
        mock_fn = AsyncMock(
            side_effect=[
                sqlite3.OperationalError("database is locked"),
                sqlite3.OperationalError("database is busy"),
                sqlite3.OperationalError("database is locked"),
                "success",
            ]
        )
        result = await execute_with_retry(mock_fn, initial_wait=0.01, max_wait=0.02)
        assert result == "success"
        assert mock_fn.call_count == 4

    async def test_raises_after_max_attempts(self):
        """Should raise exception after exhausting retries."""
        mock_fn = AsyncMock(side_effect=sqlite3.OperationalError("database is locked"))
        with pytest.raises(sqlite3.OperationalError, match="database is locked"):
            await execute_with_retry(
                mock_fn, max_attempts=3, initial_wait=0.01, max_wait=0.02
            )
        assert mock_fn.call_count == 3

    async def test_does_not_retry_non_busy_error(self):
        """Should not retry on non-busy/locked errors."""
        mock_fn = AsyncMock(side_effect=sqlite3.OperationalError("no such table: foo"))
        with pytest.raises(sqlite3.OperationalError, match="no such table"):
            await execute_with_retry(mock_fn, initial_wait=0.01)
        mock_fn.assert_called_once()

    async def test_does_not_retry_non_operational_error(self):
        """Should not retry on non-OperationalError exceptions."""
        mock_fn = AsyncMock(side_effect=ValueError("some error"))
        with pytest.raises(ValueError, match="some error"):
            await execute_with_retry(mock_fn, initial_wait=0.01)
        mock_fn.assert_called_once()
