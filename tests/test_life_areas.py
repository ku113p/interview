"""Unit tests for LifeAreasManager."""

import pytest
from src.infrastructure.db import managers as db
from src.shared.ids import new_id


class TestGetDescendants:
    """Test the get_descendants recursive CTE query."""

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_get_descendants_ordered_by_title(self, temp_db):
        """Should return descendants sorted alphabetically by title."""
        # Arrange
        user_id = new_id()
        parent_id = new_id()
        parent = db.LifeArea(
            id=parent_id, title="Parent", parent_id=None, user_id=user_id
        )
        await db.LifeAreasManager.create(parent_id, parent)

        # Create children in non-alphabetical order
        for title in ["Zebra", "Apple", "Mango"]:
            child_id = new_id()
            child = db.LifeArea(
                id=child_id, title=title, parent_id=parent_id, user_id=user_id
            )
            await db.LifeAreasManager.create(child_id, child)

        # Act
        descendants = await db.LifeAreasManager.get_descendants(parent_id)

        # Assert - should be alphabetically sorted
        titles = [d.title for d in descendants]
        assert titles == ["Apple", "Mango", "Zebra"]

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
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
