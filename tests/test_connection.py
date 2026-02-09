"""Unit tests for database connection and transaction handling."""

import pytest
from src.infrastructure.db import managers as db
from src.infrastructure.db.connection import get_connection, transaction
from src.shared.ids import new_id


class TestTransaction:
    """Test the transaction context manager."""

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_wal_mode_enabled(self, temp_db):
        """WAL journal mode should be enabled."""
        async with get_connection() as conn:
            cursor = await conn.execute("PRAGMA journal_mode")
            row = await cursor.fetchone()
            assert row[0].lower() == "wal"

    @pytest.mark.asyncio
    async def test_busy_timeout_set(self, temp_db):
        """Busy timeout should be set to 30 seconds."""
        async with get_connection() as conn:
            cursor = await conn.execute("PRAGMA busy_timeout")
            row = await cursor.fetchone()
            assert row[0] == 30000
