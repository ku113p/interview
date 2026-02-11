"""Area loop business logic methods."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

import aiosqlite

from src.infrastructure.db import managers as db
from src.shared.ids import new_id

if TYPE_CHECKING:
    from src.workflows.subgraphs.area_loop.tools import SubAreaNode

MAX_SUBTREE_DEPTH = 5


def _str_to_uuid(value: str | None) -> uuid.UUID | None:
    """Convert string to UUID, returning None if input is None or 'root'."""
    if value is None or value == "root":
        return None
    return uuid.UUID(value)


class LifeAreaMethods:
    """CRUD operations for life areas."""

    @staticmethod
    async def list(
        user_id: str, conn: aiosqlite.Connection | None = None
    ) -> list[db.LifeArea]:
        u_id = _str_to_uuid(user_id)
        if u_id is None:
            return []
        return await db.LifeAreasManager.list_by_user(u_id, conn=conn)

    @staticmethod
    async def get(
        user_id: str, area_id: str, conn: aiosqlite.Connection | None = None
    ) -> db.LifeArea:
        u_id = _str_to_uuid(user_id)
        a_id = _str_to_uuid(area_id)

        if u_id is None or a_id is None:
            raise KeyError("user_id and area_id are required")

        area = await db.LifeAreasManager.get_by_id(a_id, conn=conn)
        if area is None:
            raise KeyError(f"LifeArea {area_id} not found")

        if area.user_id != u_id:
            raise KeyError(f"LifeArea {area_id} does not belong to user {user_id}")

        return area

    @staticmethod
    async def create(
        user_id: str,
        title: str,
        parent_id: str | None = None,
        conn: aiosqlite.Connection | None = None,
    ) -> db.LifeArea:
        u_id = _str_to_uuid(user_id)
        p_id = _str_to_uuid(parent_id)

        if u_id is None:
            raise KeyError("user_id is required")

        # Validate parent exists and belongs to same user
        if p_id is not None:
            parent = await db.LifeAreasManager.get_by_id(p_id, conn=conn)
            if parent is None:
                raise KeyError(f"Parent area {parent_id} not found")
            if parent.user_id != u_id:
                raise KeyError(f"Parent area {parent_id} does not belong to user")

        area_id = new_id()
        area = db.LifeArea(id=area_id, title=title, parent_id=p_id, user_id=u_id)
        await db.LifeAreasManager.create(area_id, area, conn=conn)
        return area

    @staticmethod
    async def create_subtree(
        user_id: str,
        parent_id: str,
        subtree: list[SubAreaNode | dict[str, Any]],
        conn: aiosqlite.Connection | None = None,
        _depth: int = 0,
    ) -> list[db.LifeArea]:
        """Recursively create a subtree of areas under a parent.

        Args:
            user_id: UUID of the user
            parent_id: UUID of the parent area to attach subtree to
            subtree: List of SubAreaNode dicts with 'title' and optional 'children'
            conn: Optional database connection
            _depth: Internal recursion depth counter (do not set manually)

        Returns:
            List of all created LifeArea objects (flattened)

        Raises:
            ValueError: If maximum nesting depth is exceeded
            TypeError: If node is not a SubAreaNode or dict
        """
        if _depth >= MAX_SUBTREE_DEPTH:
            raise ValueError(f"Maximum nesting depth ({MAX_SUBTREE_DEPTH}) exceeded")

        created: list[db.LifeArea] = []

        for node in subtree:
            # Import here to avoid circular import at module level
            from src.workflows.subgraphs.area_loop.tools import SubAreaNode

            if not isinstance(node, (SubAreaNode, dict)):
                raise TypeError(
                    f"Expected SubAreaNode or dict, got {type(node).__name__}"
                )

            title = node.title if hasattr(node, "title") else node["title"]
            children = (
                node.children if hasattr(node, "children") else node.get("children", [])
            )

            area = await LifeAreaMethods.create(user_id, title, parent_id, conn=conn)
            created.append(area)

            if children:
                child_areas = await LifeAreaMethods.create_subtree(
                    user_id, str(area.id), children, conn=conn, _depth=_depth + 1
                )
                created.extend(child_areas)

        return created

    @staticmethod
    async def _validate_new_parent(
        area_id: uuid.UUID,
        new_parent_id: uuid.UUID,
        user_id: uuid.UUID,
        parent_id_str: str,
        conn: aiosqlite.Connection | None,
    ) -> None:
        """Validate new parent exists, belongs to user, and won't create cycle."""
        parent = await db.LifeAreasManager.get_by_id(new_parent_id, conn=conn)
        if parent is None:
            raise KeyError(f"Parent area {parent_id_str} not found")
        if parent.user_id != user_id:
            raise KeyError(f"Parent area {parent_id_str} does not belong to user")
        if await db.LifeAreasManager.would_create_cycle(area_id, new_parent_id, conn):
            raise ValueError(
                f"Cannot set {parent_id_str} as parent: would create a cycle"
            )

    @staticmethod
    async def update(
        user_id: str,
        area_id: str,
        title: str | None = None,
        parent_id: str | None = None,
        conn: aiosqlite.Connection | None = None,
    ) -> db.LifeArea:
        """Update an area's title and/or parent."""
        area = await LifeAreaMethods.get(user_id, area_id, conn=conn)
        u_id = uuid.UUID(user_id)
        new_parent_id = _str_to_uuid(parent_id)

        # Validate new parent if changing
        if new_parent_id is not None and new_parent_id != area.parent_id:
            await LifeAreaMethods._validate_new_parent(
                area.id, new_parent_id, u_id, str(new_parent_id), conn
            )

        updated_area = db.LifeArea(
            id=area.id,
            title=title if title is not None else area.title,
            parent_id=new_parent_id if parent_id is not None else area.parent_id,
            user_id=area.user_id,
        )
        await db.LifeAreasManager.update(area.id, updated_area, conn=conn)
        return updated_area

    @staticmethod
    async def delete(
        user_id: str, area_id: str, conn: aiosqlite.Connection | None = None
    ) -> None:
        u_id = _str_to_uuid(user_id)
        a_id = _str_to_uuid(area_id)

        if u_id is None or a_id is None:
            raise KeyError("user_id and area_id are required")

        area = await db.LifeAreasManager.get_by_id(a_id, conn=conn)
        if area is None:
            raise KeyError(f"LifeArea {area_id} not found")
        if area.user_id != u_id:
            raise KeyError(f"LifeArea {area_id} does not belong to user {user_id}")

        await db.LifeAreasManager.delete(a_id, conn=conn)


class CurrentAreaMethods:
    """Operations for managing the current interview area."""

    @staticmethod
    async def set_current(
        user_id: str, area_id: str, conn: aiosqlite.Connection | None = None
    ) -> db.LifeArea:
        """Set an area as the current area for interview."""
        # Verify area exists and belongs to user
        area = await LifeAreaMethods.get(user_id, area_id, conn=conn)

        u_id = _str_to_uuid(user_id)
        if u_id is None:
            raise KeyError("Invalid user_id")

        # Get existing user and update current_area_id
        user = await db.UsersManager.get_by_id(u_id, conn=conn)
        if user is None:
            raise KeyError(f"User {user_id} not found")

        updated_user = db.User(
            id=user.id,
            name=user.name,
            mode=user.mode,
            current_area_id=area.id,
        )
        await db.UsersManager.update(u_id, updated_user, conn=conn)
        return area
