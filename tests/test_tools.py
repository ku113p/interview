"""Unit tests for area tools."""

import pytest

from src.infrastructure.db import repositories as db
from src.shared.ids import new_id
from src.workflows.subgraphs.area_loop.tools import CurrentAreaMethods


class TestSetCurrentArea:
    """Test the set_current_area tool."""

    def test_set_current_area_success(self, temp_db, sample_user):
        """Setting current area should update user record."""
        # Arrange - create user in DB
        db.UsersManager.create(
            sample_user.id,
            db.User(
                id=sample_user.id,
                name="test",
                mode=sample_user.mode.value,
                current_area_id=None,
            ),
        )

        # Create an area for the user
        area_id = new_id()
        area = db.LifeArea(
            id=area_id,
            title="Test Area",
            parent_id=None,
            user_id=sample_user.id,
        )
        db.LifeAreaManager.create(area_id, area)

        # Act
        result = CurrentAreaMethods.set_current(str(sample_user.id), str(area_id))

        # Assert
        assert result.id == area_id
        updated_user = db.UsersManager.get_by_id(sample_user.id)
        assert updated_user is not None
        assert updated_user.current_area_id == area_id

    def test_set_current_area_invalid_area(self, temp_db, sample_user):
        """Should raise KeyError for non-existent area."""
        # Arrange - create user in DB
        db.UsersManager.create(
            sample_user.id,
            db.User(
                id=sample_user.id,
                name="test",
                mode=sample_user.mode.value,
                current_area_id=None,
            ),
        )

        fake_area_id = new_id()

        # Act & Assert
        with pytest.raises(KeyError):
            CurrentAreaMethods.set_current(str(sample_user.id), str(fake_area_id))

    def test_set_current_area_wrong_user(self, temp_db, sample_user):
        """Should raise KeyError when area belongs to different user."""
        # Arrange - create user in DB
        db.UsersManager.create(
            sample_user.id,
            db.User(
                id=sample_user.id,
                name="test",
                mode=sample_user.mode.value,
                current_area_id=None,
            ),
        )

        # Create another user who owns the area
        other_user_id = new_id()
        db.UsersManager.create(
            other_user_id,
            db.User(
                id=other_user_id,
                name="other",
                mode="auto",
                current_area_id=None,
            ),
        )

        # Create an area owned by the other user
        area_id = new_id()
        area = db.LifeArea(
            id=area_id,
            title="Other's Area",
            parent_id=None,
            user_id=other_user_id,
        )
        db.LifeAreaManager.create(area_id, area)

        # Act & Assert - sample_user tries to set other_user's area as current
        with pytest.raises(KeyError):
            CurrentAreaMethods.set_current(str(sample_user.id), str(area_id))
