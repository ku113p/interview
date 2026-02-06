"""Unit tests for session helpers."""

from src.adapters.cli.session import ensure_user
from src.domain.models import InputMode
from src.infrastructure.db import repositories as db
from src.shared.ids import new_id


class TestEnsureUser:
    """Test the ensure_user function with current_area_id handling."""

    def test_returns_current_area_when_set(self, temp_db):
        """Should return user's current_area_id when set."""
        # Arrange - create user with current_area_id set
        user_id = new_id()
        area_id = new_id()

        # Create area first
        area = db.LifeArea(
            id=area_id,
            title="Test Area",
            parent_id=None,
            user_id=user_id,
        )
        db.LifeAreaManager.create(area_id, area)

        # Create user with current_area_id
        db.UsersManager.create(
            user_id,
            db.User(
                id=user_id,
                name="test",
                mode="auto",
                current_area_id=area_id,
            ),
        )

        # Act
        user, current_area_id = ensure_user(user_id)

        # Assert
        assert user.id == user_id
        assert current_area_id == area_id

    def test_returns_none_when_not_set(self, temp_db):
        """Should return None when no current_area_id."""
        # Arrange - create user without current_area_id
        user_id = new_id()
        db.UsersManager.create(
            user_id,
            db.User(
                id=user_id,
                name="test",
                mode="auto",
                current_area_id=None,
            ),
        )

        # Act
        user, current_area_id = ensure_user(user_id)

        # Assert
        assert user.id == user_id
        assert current_area_id is None

    def test_returns_none_for_new_user(self, temp_db):
        """Should return None for newly created user."""
        # Arrange - new user_id that doesn't exist
        user_id = new_id()

        # Act
        user, current_area_id = ensure_user(user_id)

        # Assert
        assert user.id == user_id
        assert user.mode == InputMode.auto
        assert current_area_id is None

        # Verify user was created in DB
        db_user = db.UsersManager.get_by_id(user_id)
        assert db_user is not None
        assert db_user.name == "cli"
