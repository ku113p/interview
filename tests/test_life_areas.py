"""Unit tests for LifeAreasManager."""

import pytest
from src.infrastructure.db import managers as db
from src.shared.ids import new_id
from src.workflows.subgraphs.area_loop.methods import LifeAreaMethods


class TestGetDescendants:
    """Test the get_descendants recursive CTE query."""

    async def test_get_descendants_empty(self, temp_db):
        """Should return empty list when area has no children."""
        # Arrange
        user_id = new_id()
        area_id = new_id()
        area = db.LifeArea(id=area_id, title="Parent", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)

        # Act
        descendants = await db.LifeAreasManager.get_descendants(area_id)

        # Assert
        assert descendants == []

    async def test_get_descendants_direct_children(self, temp_db):
        """Should return direct children of the area."""
        # Arrange
        user_id = new_id()
        parent_id = new_id()
        parent = db.LifeArea(
            id=parent_id, title="Parent", parent_id=None, user_id=user_id
        )
        await db.LifeAreasManager.create(parent_id, parent)

        child1_id = new_id()
        child1 = db.LifeArea(
            id=child1_id, title="Child A", parent_id=parent_id, user_id=user_id
        )
        await db.LifeAreasManager.create(child1_id, child1)

        child2_id = new_id()
        child2 = db.LifeArea(
            id=child2_id, title="Child B", parent_id=parent_id, user_id=user_id
        )
        await db.LifeAreasManager.create(child2_id, child2)

        # Act
        descendants = await db.LifeAreasManager.get_descendants(parent_id)

        # Assert
        assert len(descendants) == 2
        titles = [d.title for d in descendants]
        assert "Child A" in titles
        assert "Child B" in titles

    async def test_get_descendants_nested_hierarchy(self, temp_db):
        """Should return all descendants recursively at any depth."""
        # Arrange: Create a 3-level hierarchy
        #   Parent
        #   ├── Child1
        #   │   └── Grandchild1
        #   └── Child2
        user_id = new_id()

        parent_id = new_id()
        parent = db.LifeArea(
            id=parent_id, title="Parent", parent_id=None, user_id=user_id
        )
        await db.LifeAreasManager.create(parent_id, parent)

        child1_id = new_id()
        child1 = db.LifeArea(
            id=child1_id, title="Child1", parent_id=parent_id, user_id=user_id
        )
        await db.LifeAreasManager.create(child1_id, child1)

        child2_id = new_id()
        child2 = db.LifeArea(
            id=child2_id, title="Child2", parent_id=parent_id, user_id=user_id
        )
        await db.LifeAreasManager.create(child2_id, child2)

        grandchild_id = new_id()
        grandchild = db.LifeArea(
            id=grandchild_id, title="Grandchild1", parent_id=child1_id, user_id=user_id
        )
        await db.LifeAreasManager.create(grandchild_id, grandchild)

        # Act
        descendants = await db.LifeAreasManager.get_descendants(parent_id)

        # Assert - should include all 3 descendants
        assert len(descendants) == 3
        titles = [d.title for d in descendants]
        assert "Child1" in titles
        assert "Child2" in titles
        assert "Grandchild1" in titles

    async def test_get_descendants_ordered_by_id(self, temp_db):
        """Should return descendants sorted by UUID7 (creation order)."""
        # Arrange
        user_id = new_id()
        parent_id = new_id()
        parent = db.LifeArea(
            id=parent_id, title="Parent", parent_id=None, user_id=user_id
        )
        await db.LifeAreasManager.create(parent_id, parent)

        # Create children in specific order
        for title in ["Zebra", "Apple", "Mango"]:
            child_id = new_id()
            child = db.LifeArea(
                id=child_id, title=title, parent_id=parent_id, user_id=user_id
            )
            await db.LifeAreasManager.create(child_id, child)

        # Act
        descendants = await db.LifeAreasManager.get_descendants(parent_id)

        # Assert - should be sorted by UUID7 (creation order)
        titles = [d.title for d in descendants]
        assert titles == ["Zebra", "Apple", "Mango"]

    async def test_get_descendants_does_not_include_parent(self, temp_db):
        """Should not include the parent area itself in results."""
        # Arrange
        user_id = new_id()
        parent_id = new_id()
        parent = db.LifeArea(
            id=parent_id, title="Parent", parent_id=None, user_id=user_id
        )
        await db.LifeAreasManager.create(parent_id, parent)

        child_id = new_id()
        child = db.LifeArea(
            id=child_id, title="Child", parent_id=parent_id, user_id=user_id
        )
        await db.LifeAreasManager.create(child_id, child)

        # Act
        descendants = await db.LifeAreasManager.get_descendants(parent_id)

        # Assert
        assert len(descendants) == 1
        assert descendants[0].id == child_id
        assert parent_id not in [d.id for d in descendants]

    async def test_get_descendants_does_not_include_siblings(self, temp_db):
        """Should only return descendants, not siblings or other branches."""
        # Arrange: Create two separate branches
        #   Root
        #   ├── BranchA
        #   │   └── LeafA
        #   └── BranchB
        #       └── LeafB
        user_id = new_id()

        root_id = new_id()
        root = db.LifeArea(id=root_id, title="Root", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(root_id, root)

        branch_a_id = new_id()
        branch_a = db.LifeArea(
            id=branch_a_id, title="BranchA", parent_id=root_id, user_id=user_id
        )
        await db.LifeAreasManager.create(branch_a_id, branch_a)

        branch_b_id = new_id()
        branch_b = db.LifeArea(
            id=branch_b_id, title="BranchB", parent_id=root_id, user_id=user_id
        )
        await db.LifeAreasManager.create(branch_b_id, branch_b)

        leaf_a_id = new_id()
        leaf_a = db.LifeArea(
            id=leaf_a_id, title="LeafA", parent_id=branch_a_id, user_id=user_id
        )
        await db.LifeAreasManager.create(leaf_a_id, leaf_a)

        leaf_b_id = new_id()
        leaf_b = db.LifeArea(
            id=leaf_b_id, title="LeafB", parent_id=branch_b_id, user_id=user_id
        )
        await db.LifeAreasManager.create(leaf_b_id, leaf_b)

        # Act - get descendants of BranchA only
        descendants = await db.LifeAreasManager.get_descendants(branch_a_id)

        # Assert - should only include LeafA, not BranchB or LeafB
        assert len(descendants) == 1
        assert descendants[0].title == "LeafA"


class TestGetAncestors:
    """Test the get_ancestors recursive CTE query."""

    async def test_get_ancestors_empty_for_root(self, temp_db):
        """Should return empty list for root area (no parent)."""
        # Arrange
        user_id = new_id()
        area_id = new_id()
        area = db.LifeArea(id=area_id, title="Root", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)

        # Act
        ancestors = await db.LifeAreasManager.get_ancestors(area_id)

        # Assert
        assert ancestors == []

    async def test_get_ancestors_returns_parent(self, temp_db):
        """Should return direct parent."""
        # Arrange
        user_id = new_id()
        parent_id = new_id()
        parent = db.LifeArea(
            id=parent_id, title="Parent", parent_id=None, user_id=user_id
        )
        await db.LifeAreasManager.create(parent_id, parent)

        child_id = new_id()
        child = db.LifeArea(
            id=child_id, title="Child", parent_id=parent_id, user_id=user_id
        )
        await db.LifeAreasManager.create(child_id, child)

        # Act
        ancestors = await db.LifeAreasManager.get_ancestors(child_id)

        # Assert
        assert len(ancestors) == 1
        assert ancestors[0].id == parent_id

    async def test_get_ancestors_full_chain(self, temp_db):
        """Should return full ancestor chain from leaf to root."""
        # Arrange: Grandparent -> Parent -> Child
        user_id = new_id()

        grandparent_id = new_id()
        grandparent = db.LifeArea(
            id=grandparent_id, title="Grandparent", parent_id=None, user_id=user_id
        )
        await db.LifeAreasManager.create(grandparent_id, grandparent)

        parent_id = new_id()
        parent = db.LifeArea(
            id=parent_id, title="Parent", parent_id=grandparent_id, user_id=user_id
        )
        await db.LifeAreasManager.create(parent_id, parent)

        child_id = new_id()
        child = db.LifeArea(
            id=child_id, title="Child", parent_id=parent_id, user_id=user_id
        )
        await db.LifeAreasManager.create(child_id, child)

        # Act
        ancestors = await db.LifeAreasManager.get_ancestors(child_id)

        # Assert - should include Parent and Grandparent
        assert len(ancestors) == 2
        ancestor_ids = [a.id for a in ancestors]
        assert parent_id in ancestor_ids
        assert grandparent_id in ancestor_ids


class TestWouldCreateCycle:
    """Test the would_create_cycle validation method."""

    async def test_self_reference_is_cycle(self, temp_db):
        """Setting parent to self should be detected as cycle."""
        # Arrange
        user_id = new_id()
        area_id = new_id()
        area = db.LifeArea(id=area_id, title="Area", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)

        # Act
        is_cycle = await db.LifeAreasManager.would_create_cycle(area_id, area_id)

        # Assert
        assert is_cycle is True

    async def test_descendant_as_parent_is_cycle(self, temp_db):
        """Setting child as parent of its ancestor should be cycle."""
        # Arrange: Parent -> Child
        user_id = new_id()

        parent_id = new_id()
        parent = db.LifeArea(
            id=parent_id, title="Parent", parent_id=None, user_id=user_id
        )
        await db.LifeAreasManager.create(parent_id, parent)

        child_id = new_id()
        child = db.LifeArea(
            id=child_id, title="Child", parent_id=parent_id, user_id=user_id
        )
        await db.LifeAreasManager.create(child_id, child)

        # Act - try to make Parent's parent be Child (would create cycle)
        is_cycle = await db.LifeAreasManager.would_create_cycle(parent_id, child_id)

        # Assert
        assert is_cycle is True

    async def test_valid_parent_is_not_cycle(self, temp_db):
        """Setting a non-descendant as parent should not be cycle."""
        # Arrange: Two separate areas
        user_id = new_id()

        area_a_id = new_id()
        area_a = db.LifeArea(
            id=area_a_id, title="Area A", parent_id=None, user_id=user_id
        )
        await db.LifeAreasManager.create(area_a_id, area_a)

        area_b_id = new_id()
        area_b = db.LifeArea(
            id=area_b_id, title="Area B", parent_id=None, user_id=user_id
        )
        await db.LifeAreasManager.create(area_b_id, area_b)

        # Act - A can have B as parent (no cycle)
        is_cycle = await db.LifeAreasManager.would_create_cycle(area_a_id, area_b_id)

        # Assert
        assert is_cycle is False


class TestLifeAreaMethodsCreate:
    """Test parent validation in LifeAreaMethods.create."""

    async def test_create_with_valid_parent(self, temp_db, sample_user):
        """Should create area when parent exists and belongs to user."""
        # Arrange
        parent = await LifeAreaMethods.create(str(sample_user.id), "Parent")

        # Act
        child = await LifeAreaMethods.create(
            str(sample_user.id), "Child", str(parent.id)
        )

        # Assert
        assert child.parent_id == parent.id
        assert child.user_id == sample_user.id

    async def test_create_with_nonexistent_parent_fails(self, temp_db, sample_user):
        """Should raise KeyError when parent doesn't exist."""
        fake_parent_id = str(new_id())

        with pytest.raises(KeyError, match="not found"):
            await LifeAreaMethods.create(str(sample_user.id), "Child", fake_parent_id)

    async def test_create_with_other_users_parent_fails(self, temp_db, sample_user):
        """Should raise KeyError when parent belongs to different user."""
        # Arrange - create area for different user
        other_user_id = new_id()
        other_user = db.User(id=other_user_id, name="Other", mode="auto")
        await db.UsersManager.create(other_user_id, other_user)

        other_area = await LifeAreaMethods.create(str(other_user_id), "Other's Area")

        # Act & Assert - sample_user can't use other's area as parent
        with pytest.raises(KeyError, match="does not belong to user"):
            await LifeAreaMethods.create(
                str(sample_user.id), "Child", str(other_area.id)
            )


class TestLifeAreaMethodsUpdate:
    """Test LifeAreaMethods.update with cycle validation."""

    async def test_update_title_success(self, temp_db, sample_user):
        """Should update area title."""
        area = await LifeAreaMethods.create(str(sample_user.id), "Original")

        updated = await LifeAreaMethods.update(
            str(sample_user.id), str(area.id), title="New Title"
        )

        assert updated.title == "New Title"
        assert updated.id == area.id

    async def test_update_parent_success(self, temp_db, sample_user):
        """Should update area parent when valid."""
        parent = await LifeAreaMethods.create(str(sample_user.id), "Parent")
        child = await LifeAreaMethods.create(str(sample_user.id), "Child")
        assert child.parent_id is None

        updated = await LifeAreaMethods.update(
            str(sample_user.id), str(child.id), parent_id=str(parent.id)
        )

        assert updated.parent_id == parent.id

    async def test_update_parent_cycle_fails(self, temp_db, sample_user):
        """Should raise ValueError when update would create cycle."""
        # Arrange: Parent -> Child
        parent = await LifeAreaMethods.create(str(sample_user.id), "Parent")
        child = await LifeAreaMethods.create(
            str(sample_user.id), "Child", str(parent.id)
        )

        # Act & Assert: try to make Parent's parent be Child
        with pytest.raises(ValueError, match="would create a cycle"):
            await LifeAreaMethods.update(
                str(sample_user.id), str(parent.id), parent_id=str(child.id)
            )

    async def test_update_self_parent_fails(self, temp_db, sample_user):
        """Should raise ValueError when setting self as parent."""
        area = await LifeAreaMethods.create(str(sample_user.id), "Area")

        with pytest.raises(ValueError, match="would create a cycle"):
            await LifeAreaMethods.update(
                str(sample_user.id), str(area.id), parent_id=str(area.id)
            )

    async def test_update_grandchild_as_parent_fails(self, temp_db, sample_user):
        """Should detect cycle through grandchild."""
        # Arrange: Grandparent -> Parent -> Child
        grandparent = await LifeAreaMethods.create(str(sample_user.id), "Grandparent")
        parent = await LifeAreaMethods.create(
            str(sample_user.id), "Parent", str(grandparent.id)
        )
        child = await LifeAreaMethods.create(
            str(sample_user.id), "Child", str(parent.id)
        )

        # Act & Assert: try to make Grandparent's parent be Child
        with pytest.raises(ValueError, match="would create a cycle"):
            await LifeAreaMethods.update(
                str(sample_user.id), str(grandparent.id), parent_id=str(child.id)
            )

    async def test_update_other_users_area_fails(self, temp_db, sample_user):
        """Should raise KeyError when updating another user's area."""
        other_user_id = new_id()
        other_user = db.User(id=other_user_id, name="Other", mode="auto")
        await db.UsersManager.create(other_user_id, other_user)
        other_area = await LifeAreaMethods.create(str(other_user_id), "Other's Area")

        with pytest.raises(KeyError, match="does not belong to user"):
            await LifeAreaMethods.update(
                str(sample_user.id), str(other_area.id), title="Hacked"
            )
