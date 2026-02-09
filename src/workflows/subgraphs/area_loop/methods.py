"""Area loop business logic methods."""

import uuid

import aiosqlite

from src.infrastructure.db import managers as db
from src.shared.ids import new_id


def _str_to_uuid(value: str | None) -> uuid.UUID | None:
    """Convert string to UUID, returning None if input is None."""
    if value is None:
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

        area_id = new_id()
        area = db.LifeArea(id=area_id, title=title, parent_id=p_id, user_id=u_id)
        await db.LifeAreasManager.create(area_id, area, conn=conn)
        return area

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


class CriteriaMethods:
    """CRUD operations for criteria."""

    @staticmethod
    async def list(
        user_id: str, area_id: str, conn: aiosqlite.Connection | None = None
    ) -> list[db.Criteria]:
        # Verify user owns the area first
        area = await LifeAreaMethods.get(user_id, area_id, conn=conn)
        return await db.CriteriaManager.list_by_area(area.id, conn=conn)

    @staticmethod
    async def delete(
        user_id: str, criteria_id: str, conn: aiosqlite.Connection | None = None
    ) -> None:
        u_id = _str_to_uuid(user_id)
        c_id = _str_to_uuid(criteria_id)
        if u_id is None or c_id is None:
            raise KeyError("user_id and criteria_id are required")
        criteria = await db.CriteriaManager.get_by_id(c_id, conn=conn)
        if criteria is None:
            raise KeyError(f"Criteria {criteria_id} not found")
        area = await LifeAreaMethods.get(user_id, str(criteria.area_id), conn=conn)
        if area.user_id != u_id:
            raise KeyError(f"Criteria {criteria_id} does not belong to user {user_id}")
        await db.CriteriaManager.delete(c_id, conn=conn)

    @staticmethod
    async def create(
        user_id: str,
        area_id: str,
        title: str,
        conn: aiosqlite.Connection | None = None,
    ) -> db.Criteria:
        area = await LifeAreaMethods.get(user_id, area_id, conn=conn)

        criteria_id = new_id()
        criteria = db.Criteria(id=criteria_id, title=title, area_id=area.id)
        await db.CriteriaManager.create(criteria_id, criteria, conn=conn)
        return criteria


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
