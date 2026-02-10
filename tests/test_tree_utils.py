"""Unit tests for tree_utils module."""

import uuid

from src.infrastructure.db.models import LifeArea
from src.shared.tree_utils import build_sub_area_info, build_tree_text


def _make_area(
    title: str,
    parent_id: uuid.UUID | None,
    area_id: uuid.UUID | None = None,
) -> LifeArea:
    """Helper to create LifeArea for testing."""
    return LifeArea(
        id=area_id or uuid.uuid4(),
        title=title,
        parent_id=parent_id,
        user_id=uuid.uuid4(),
    )


class TestBuildTreeText:
    def test_empty_list(self):
        """Empty list returns empty string."""
        result = build_tree_text([], uuid.uuid4())
        assert result == ""

    def test_single_level(self):
        """Direct children render at root level."""
        root_id = uuid.uuid4()
        areas = [
            _make_area("Work", root_id),
            _make_area("Education", root_id),
        ]
        result = build_tree_text(areas, root_id)
        assert result == "Education\nWork"  # Alphabetical

    def test_nested_hierarchy(self):
        """Multi-level nesting shows proper indentation."""
        root_id = uuid.uuid4()
        work_id = uuid.uuid4()
        areas = [
            _make_area("Work", root_id, work_id),
            _make_area("Projects", work_id),
            _make_area("Skills", work_id),
        ]
        result = build_tree_text(areas, root_id)
        expected = "Work\n  Projects\n  Skills"
        assert result == expected

    def test_multiple_branches(self):
        """Multiple top-level branches with children."""
        root_id = uuid.uuid4()
        work_id = uuid.uuid4()
        hobby_id = uuid.uuid4()
        areas = [
            _make_area("Work", root_id, work_id),
            _make_area("Projects", work_id),
            _make_area("Hobbies", root_id, hobby_id),
            _make_area("Gaming", hobby_id),
        ]
        result = build_tree_text(areas, root_id)
        expected = "Hobbies\n  Gaming\nWork\n  Projects"
        assert result == expected

    def test_custom_indent(self):
        """Custom indentation string is used."""
        root_id = uuid.uuid4()
        work_id = uuid.uuid4()
        areas = [
            _make_area("Work", root_id, work_id),
            _make_area("Projects", work_id),
        ]
        result = build_tree_text(areas, root_id, indent="    ")
        expected = "Work\n    Projects"
        assert result == expected


class TestBuildSubAreaInfo:
    def test_empty_list(self):
        """Empty list returns empty list."""
        result = build_sub_area_info([], uuid.uuid4())
        assert result == []

    def test_single_level_paths(self):
        """Direct children have simple paths (just title)."""
        root_id = uuid.uuid4()
        areas = [
            _make_area("Work", root_id),
            _make_area("Education", root_id),
        ]
        result = build_sub_area_info(areas, root_id)
        paths = [info.path for info in result]
        assert set(paths) == {"Work", "Education"}

    def test_nested_paths(self):
        """Nested children include parent in path."""
        root_id = uuid.uuid4()
        work_id = uuid.uuid4()
        areas = [
            _make_area("Work", root_id, work_id),
            _make_area("Projects", work_id),
        ]
        result = build_sub_area_info(areas, root_id)
        paths = [info.path for info in result]
        assert set(paths) == {"Work", "Work > Projects"}

    def test_duplicate_titles_unique_paths(self):
        """Same title under different parents have unique paths."""
        root_id = uuid.uuid4()
        work_id = uuid.uuid4()
        hobby_id = uuid.uuid4()
        areas = [
            _make_area("Work", root_id, work_id),
            _make_area("Skills", work_id),  # Work > Skills
            _make_area("Hobbies", root_id, hobby_id),
            _make_area("Skills", hobby_id),  # Hobbies > Skills
        ]
        result = build_sub_area_info(areas, root_id)
        paths = [info.path for info in result]
        assert "Work > Skills" in paths
        assert "Hobbies > Skills" in paths

    def test_deep_nesting(self):
        """Three levels of nesting produce correct paths."""
        root_id = uuid.uuid4()
        work_id = uuid.uuid4()
        projects_id = uuid.uuid4()
        areas = [
            _make_area("Work", root_id, work_id),
            _make_area("Projects", work_id, projects_id),
            _make_area("Backend", projects_id),
        ]
        result = build_sub_area_info(areas, root_id)
        paths = [info.path for info in result]
        assert set(paths) == {"Work", "Work > Projects", "Work > Projects > Backend"}

    def test_info_contains_original_area(self):
        """SubAreaInfo contains reference to original LifeArea."""
        root_id = uuid.uuid4()
        work_id = uuid.uuid4()
        work_area = _make_area("Work", root_id, work_id)
        areas = [work_area]
        result = build_sub_area_info(areas, root_id)
        assert len(result) == 1
        assert result[0].area is work_area
        assert result[0].path == "Work"
