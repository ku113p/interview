"""Utilities for building tree representations from flat LifeArea lists."""

import uuid
from dataclasses import dataclass

from src.infrastructure.db.models import LifeArea


@dataclass
class SubAreaInfo:
    """Sub-area with its hierarchical path."""

    area: LifeArea
    path: str  # e.g., "Work > Projects"


def build_sub_area_info(
    areas: list[LifeArea],
    root_parent_id: uuid.UUID,
) -> list[SubAreaInfo]:
    """Build SubAreaInfo list with paths from flat LifeArea list.

    Args:
        areas: Flat list from get_descendants()
        root_parent_id: The area_id that was queried (parent of direct children)

    Returns:
        List of SubAreaInfo with paths like "Work > Projects"
    """
    if not areas:
        return []

    # Build lookup by id
    by_id: dict[uuid.UUID, LifeArea] = {a.id: a for a in areas}

    def get_path(area: LifeArea) -> str:
        """Build path from area to root, e.g., 'Work > Projects'."""
        parts = [area.title]
        current = area
        # Walk up the tree until we hit a direct child of root
        while current.parent_id and current.parent_id != root_parent_id:
            parent = by_id.get(current.parent_id)
            if parent is None:
                break
            parts.insert(0, parent.title)
            current = parent
        return " > ".join(parts)

    return [SubAreaInfo(area=a, path=get_path(a)) for a in areas]


def build_tree_text(
    areas: list[LifeArea],
    root_parent_id: uuid.UUID,
    indent: str = "  ",
) -> str:
    """Build indented tree text from flat LifeArea list.

    Args:
        areas: Flat list from get_descendants()
        root_parent_id: The area_id that was queried
        indent: Indentation string per level

    Returns:
        Indented tree like:
        Work
          Projects
          Skills
        Education
    """
    if not areas:
        return ""

    # Build parent -> children lookup
    children: dict[uuid.UUID | None, list[LifeArea]] = {}
    for area in areas:
        pid = area.parent_id
        if pid not in children:
            children[pid] = []
        children[pid].append(area)

    # Sort children alphabetically at each level
    for kids in children.values():
        kids.sort(key=lambda a: a.title)

    def render(parent_id: uuid.UUID, depth: int) -> list[str]:
        lines = []
        for area in children.get(parent_id, []):
            lines.append(f"{indent * depth}{area.title}")
            lines.extend(render(area.id, depth + 1))
        return lines

    # Start from direct children of root_parent_id
    return "\n".join(render(root_parent_id, 0))
