"""Unit tests for area tools."""

import pytest
from src.infrastructure.db import managers as db
from src.shared.ids import new_id
from src.workflows.subgraphs.area_loop.methods import MAX_SUBTREE_DEPTH, LifeAreaMethods
from src.workflows.subgraphs.area_loop.tools import (
    CurrentAreaMethods,
    SubAreaNode,
    _validate_uuid,
)


class TestValidateUuid:
    """Test the _validate_uuid function."""

    def test_valid_uuid_returns_normalized(self):
        """Valid UUID should be returned in normalized lowercase format."""
        result = _validate_uuid("0698C4A9-6BA3-7079-8000-A098A56ECCCA")
        assert result == "0698c4a9-6ba3-7079-8000-a098a56eccca"

    def test_already_normalized_uuid_unchanged(self):
        """Already normalized UUID should be returned unchanged."""
        uuid_str = "0698c4a9-6ba3-7079-8000-a098a56eccca"
        result = _validate_uuid(uuid_str)
        assert result == uuid_str

    def test_uuid_without_hyphens_normalized(self):
        """UUID without hyphens should be normalized with hyphens."""
        result = _validate_uuid("0698c4a96ba370798000a098a56eccca")
        assert result == "0698c4a9-6ba3-7079-8000-a098a56eccca"

    def test_invalid_uuid_raises_value_error(self):
        """Invalid UUID should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid UUID"):
            _validate_uuid("not-a-valid-uuid")

    def test_empty_string_raises_value_error(self):
        """Empty string should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid UUID"):
            _validate_uuid("")

    def test_mixed_case_uuid_normalized(self):
        """Mixed case UUID should be normalized to lowercase."""
        result = _validate_uuid("0698C4a9-6Ba3-7079-8000-A098a56eCCca")
        assert result == "0698c4a9-6ba3-7079-8000-a098a56eccca"


class TestSetCurrentArea:
    """Test the set_current_area tool."""

    @pytest.mark.asyncio
    async def test_set_current_area_success(self, temp_db, sample_user):
        """Setting current area should update user record."""
        # Arrange - create user in DB
        await db.UsersManager.create(
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
        await db.LifeAreasManager.create(area_id, area)

        # Act
        result = await CurrentAreaMethods.set_current(str(sample_user.id), str(area_id))

        # Assert
        assert result.id == area_id
        updated_user = await db.UsersManager.get_by_id(sample_user.id)
        assert updated_user is not None
        assert updated_user.current_area_id == area_id

    @pytest.mark.asyncio
    async def test_set_current_area_invalid_area(self, temp_db, sample_user):
        """Should raise KeyError for non-existent area."""
        # Arrange - create user in DB
        await db.UsersManager.create(
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
            await CurrentAreaMethods.set_current(str(sample_user.id), str(fake_area_id))

    @pytest.mark.asyncio
    async def test_set_current_area_wrong_user(self, temp_db, sample_user):
        """Should raise KeyError when area belongs to different user."""
        # Arrange - create user in DB
        await db.UsersManager.create(
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
        await db.UsersManager.create(
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
        await db.LifeAreasManager.create(area_id, area)

        # Act & Assert - sample_user tries to set other_user's area as current
        with pytest.raises(KeyError):
            await CurrentAreaMethods.set_current(str(sample_user.id), str(area_id))


class TestCreateSubtree:
    """Test the create_subtree tool."""

    @pytest.mark.asyncio
    async def test_create_subtree_success(self, temp_db, sample_user):
        """Creating subtree should create nested hierarchy."""
        # Arrange - create user in DB
        await db.UsersManager.create(
            sample_user.id,
            db.User(
                id=sample_user.id,
                name="test",
                mode=sample_user.mode.value,
                current_area_id=None,
            ),
        )

        # Create a parent area
        parent_id = new_id()
        parent = db.LifeArea(
            id=parent_id,
            title="Work Experience",
            parent_id=None,
            user_id=sample_user.id,
        )
        await db.LifeAreasManager.create(parent_id, parent)

        # Define subtree
        subtree = [
            SubAreaNode(
                title="Google - Engineer",
                children=[
                    SubAreaNode(title="Responsibilities"),
                    SubAreaNode(title="Achievements"),
                ],
            ),
            SubAreaNode(title="Amazon - SDE"),
        ]

        # Act
        result = await LifeAreaMethods.create_subtree(
            str(sample_user.id), str(parent_id), subtree
        )

        # Assert
        assert len(result) == 4  # Google + 2 children + Amazon
        titles = [area.title for area in result]
        assert "Google - Engineer" in titles
        assert "Responsibilities" in titles
        assert "Achievements" in titles
        assert "Amazon - SDE" in titles

        # Verify hierarchy
        google = next(a for a in result if a.title == "Google - Engineer")
        assert google.parent_id == parent_id

        resp = next(a for a in result if a.title == "Responsibilities")
        assert resp.parent_id == google.id

    @pytest.mark.asyncio
    async def test_create_subtree_invalid_parent(self, temp_db, sample_user):
        """Should raise KeyError for non-existent parent."""
        # Arrange - create user in DB
        await db.UsersManager.create(
            sample_user.id,
            db.User(
                id=sample_user.id,
                name="test",
                mode=sample_user.mode.value,
                current_area_id=None,
            ),
        )

        fake_parent_id = new_id()
        subtree = [SubAreaNode(title="Test")]

        # Act & Assert
        with pytest.raises(KeyError):
            await LifeAreaMethods.create_subtree(
                str(sample_user.id), str(fake_parent_id), subtree
            )

    @pytest.mark.asyncio
    async def test_create_subtree_empty_list(self, temp_db, sample_user):
        """Empty subtree should return empty list."""
        # Arrange - create user in DB
        await db.UsersManager.create(
            sample_user.id,
            db.User(
                id=sample_user.id,
                name="test",
                mode=sample_user.mode.value,
                current_area_id=None,
            ),
        )

        # Create a parent area
        parent_id = new_id()
        parent = db.LifeArea(
            id=parent_id,
            title="Work",
            parent_id=None,
            user_id=sample_user.id,
        )
        await db.LifeAreasManager.create(parent_id, parent)

        # Act
        result = await LifeAreaMethods.create_subtree(
            str(sample_user.id), str(parent_id), []
        )

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_create_subtree_wrong_user(self, temp_db, sample_user):
        """Should raise KeyError when parent belongs to different user."""
        # Arrange - create user in DB
        await db.UsersManager.create(
            sample_user.id,
            db.User(
                id=sample_user.id,
                name="test",
                mode=sample_user.mode.value,
                current_area_id=None,
            ),
        )

        # Create another user who owns the parent
        other_user_id = new_id()
        await db.UsersManager.create(
            other_user_id,
            db.User(
                id=other_user_id,
                name="other",
                mode="auto",
                current_area_id=None,
            ),
        )

        # Create a parent area owned by the other user
        parent_id = new_id()
        parent = db.LifeArea(
            id=parent_id,
            title="Other's Work",
            parent_id=None,
            user_id=other_user_id,
        )
        await db.LifeAreasManager.create(parent_id, parent)

        subtree = [SubAreaNode(title="Test")]

        # Act & Assert - sample_user tries to create under other_user's area
        with pytest.raises(KeyError):
            await LifeAreaMethods.create_subtree(
                str(sample_user.id), str(parent_id), subtree
            )

    @pytest.mark.asyncio
    async def test_create_subtree_deep_nesting(self, temp_db, sample_user):
        """Should handle 3+ levels of nesting."""
        # Arrange - create user in DB
        await db.UsersManager.create(
            sample_user.id,
            db.User(
                id=sample_user.id,
                name="test",
                mode=sample_user.mode.value,
                current_area_id=None,
            ),
        )

        # Create a parent area
        parent_id = new_id()
        parent = db.LifeArea(
            id=parent_id,
            title="Root",
            parent_id=None,
            user_id=sample_user.id,
        )
        await db.LifeAreasManager.create(parent_id, parent)

        # Define subtree with 3 levels
        subtree = [
            SubAreaNode(
                title="Level 1",
                children=[
                    SubAreaNode(
                        title="Level 2",
                        children=[
                            SubAreaNode(title="Level 3"),
                        ],
                    ),
                ],
            ),
        ]

        # Act
        result = await LifeAreaMethods.create_subtree(
            str(sample_user.id), str(parent_id), subtree
        )

        # Assert - all 3 levels created
        assert len(result) == 3
        titles = [area.title for area in result]
        assert "Level 1" in titles
        assert "Level 2" in titles
        assert "Level 3" in titles

        # Verify hierarchy
        level1 = next(a for a in result if a.title == "Level 1")
        level2 = next(a for a in result if a.title == "Level 2")
        level3 = next(a for a in result if a.title == "Level 3")

        assert level1.parent_id == parent_id
        assert level2.parent_id == level1.id
        assert level3.parent_id == level2.id

    @pytest.mark.asyncio
    async def test_create_subtree_depth_limit_exceeded(self, temp_db, sample_user):
        """Should raise ValueError when depth limit exceeded."""
        # Arrange - create user in DB
        await db.UsersManager.create(
            sample_user.id,
            db.User(
                id=sample_user.id,
                name="test",
                mode=sample_user.mode.value,
                current_area_id=None,
            ),
        )

        # Create a parent area
        parent_id = new_id()
        parent = db.LifeArea(
            id=parent_id,
            title="Root",
            parent_id=None,
            user_id=sample_user.id,
        )
        await db.LifeAreasManager.create(parent_id, parent)

        # Build subtree that exceeds MAX_SUBTREE_DEPTH
        def build_deep_subtree(depth: int) -> list[SubAreaNode]:
            if depth == 0:
                return []
            return [
                SubAreaNode(
                    title=f"Level {depth}",
                    children=build_deep_subtree(depth - 1),
                )
            ]

        # Create a subtree with MAX_SUBTREE_DEPTH + 1 levels
        subtree = build_deep_subtree(MAX_SUBTREE_DEPTH + 1)

        # Act & Assert
        with pytest.raises(ValueError, match="Maximum nesting depth"):
            await LifeAreaMethods.create_subtree(
                str(sample_user.id), str(parent_id), subtree
            )

    @pytest.mark.asyncio
    async def test_create_subtree_invalid_node_type(self, temp_db, sample_user):
        """Should raise TypeError for invalid node types."""
        # Arrange - create user in DB
        await db.UsersManager.create(
            sample_user.id,
            db.User(
                id=sample_user.id,
                name="test",
                mode=sample_user.mode.value,
                current_area_id=None,
            ),
        )

        # Create a parent area
        parent_id = new_id()
        parent = db.LifeArea(
            id=parent_id,
            title="Root",
            parent_id=None,
            user_id=sample_user.id,
        )
        await db.LifeAreasManager.create(parent_id, parent)

        # Pass invalid node type (string instead of SubAreaNode or dict)
        subtree = ["invalid node"]

        # Act & Assert
        with pytest.raises(TypeError, match="Expected SubAreaNode or dict"):
            await LifeAreaMethods.create_subtree(
                str(sample_user.id), str(parent_id), subtree
            )
