"""Unit tests for session helpers."""

from src.adapters.cli.session import ensure_user, get_current_area_id
from src.domain.models import InputMode
from src.infrastructure.db import repositories as db
from src.shared.ids import new_id


class TestEnsureUser:
    """Test the ensure_user function."""

    def test_returns_existing_user(self, temp_db):
        """Should return existing user from database."""
        # Arrange - create user in DB
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
        user = ensure_user(user_id)

        # Assert
        assert user.id == user_id
        assert user.mode == InputMode.auto

    def test_creates_new_user(self, temp_db):
        """Should create new user if not exists."""
        # Arrange - new user_id that doesn't exist
        user_id = new_id()

        # Act
        user = ensure_user(user_id)

        # Assert
        assert user.id == user_id
        assert user.mode == InputMode.auto

        # Verify user was created in DB
        db_user = db.UsersManager.get_by_id(user_id)
        assert db_user is not None
        assert db_user.name == "cli"


class TestGetCurrentAreaId:
    """Test the get_current_area_id function."""

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
        current_area_id = get_current_area_id(user_id)

        # Assert
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
        current_area_id = get_current_area_id(user_id)

        # Assert
        assert current_area_id is None

    def test_returns_none_for_missing_user(self, temp_db):
        """Should return None when user not found."""
        # Arrange - user_id that doesn't exist
        user_id = new_id()

        # Act
        current_area_id = get_current_area_id(user_id)

        # Assert
        assert current_area_id is None
