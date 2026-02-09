"""Unit tests for CLI transport and graph worker helpers."""

import pytest
from src.application.transports import get_or_create_user
from src.application.workers.graph_worker import _init_graph_state
from src.domain import ClientMessage, User
from src.domain.models import InputMode
from src.infrastructure.db import managers as db
from src.shared.ids import new_id


class TestGetOrCreateUser:
    """Test the get_or_create_user function."""

    @pytest.mark.asyncio
    async def test_returns_existing_user(self, temp_db):
        """Should return existing user from database."""
        # Arrange - create user in DB
        user_id = new_id()
        await db.UsersManager.create(
            user_id,
            db.User(
                id=user_id,
                name="test",
                mode="auto",
                current_area_id=None,
            ),
        )

        # Act
        user = await get_or_create_user(user_id)

        # Assert
        assert user.id == user_id
        assert user.mode == InputMode.auto

    @pytest.mark.asyncio
    async def test_creates_new_user(self, temp_db):
        """Should create new user if not exists."""
        # Arrange - new user_id that doesn't exist
        user_id = new_id()

        # Act
        user = await get_or_create_user(user_id)

        # Assert
        assert user.id == user_id
        assert user.mode == InputMode.auto

        # Verify user was created in DB
        db_user = await db.UsersManager.get_by_id(user_id)
        assert db_user is not None
        assert db_user.name == "cli"


class TestInitGraphState:
    """Test the _init_graph_state function."""

    @pytest.mark.asyncio
    async def test_uses_current_area_id_when_set(self, temp_db):
        """Should use user's current_area_id when set."""
        user_id = new_id()
        area_id = new_id()

        # Create area first
        area = db.LifeArea(
            id=area_id,
            title="Test Area",
            parent_id=None,
            user_id=user_id,
        )
        await db.LifeAreasManager.create(area_id, area)

        # Create user with current_area_id
        await db.UsersManager.create(
            user_id,
            db.User(
                id=user_id,
                name="test",
                mode="auto",
                current_area_id=area_id,
            ),
        )

        user = User(id=user_id, mode=InputMode.auto)
        msg = ClientMessage(data="test message")

        state, temp_files = await _init_graph_state(msg, user)

        assert state.area_id == area_id
        assert len(temp_files) == 2

    @pytest.mark.asyncio
    async def test_generates_new_area_id_when_not_set(self, temp_db):
        """Should generate new area_id when no current_area_id."""
        user_id = new_id()
        await db.UsersManager.create(
            user_id,
            db.User(
                id=user_id,
                name="test",
                mode="auto",
                current_area_id=None,
            ),
        )

        user = User(id=user_id, mode=InputMode.auto)
        msg = ClientMessage(data="test message")

        state, temp_files = await _init_graph_state(msg, user)

        assert state.area_id is not None
        assert len(temp_files) == 2

    @pytest.mark.asyncio
    async def test_generates_new_area_id_for_missing_user(self, temp_db):
        """Should generate new area_id when user not in database."""
        user_id = new_id()
        user = User(id=user_id, mode=InputMode.auto)
        msg = ClientMessage(data="test message")

        state, temp_files = await _init_graph_state(msg, user)

        assert state.area_id is not None
        assert len(temp_files) == 2
