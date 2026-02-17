"""Core repository managers: Users, History, LifeArea."""

import json
import uuid
from typing import Any

import aiosqlite

from .base import ORMBase
from .models import History, LifeArea, User


class UsersManager(ORMBase[User]):
    _table = "users"
    _columns = ("id", "name", "mode", "current_area_id")

    @classmethod
    def _row_to_obj(cls, row: aiosqlite.Row) -> User:
        current_area_id = row["current_area_id"]
        return User(
            id=uuid.UUID(row["id"]),
            name=row["name"],
            mode=row["mode"],
            current_area_id=uuid.UUID(current_area_id) if current_area_id else None,
        )

    @classmethod
    def _obj_to_row(cls, data: User) -> dict[str, Any]:
        return {
            "id": str(data.id),
            "name": data.name,
            "mode": data.mode,
            "current_area_id": str(data.current_area_id)
            if data.current_area_id
            else None,
        }


class HistoriesManager(ORMBase[History]):
    _table = "histories"
    _columns = ("id", "message_data", "user_id", "created_ts")
    _user_column = "user_id"

    @classmethod
    def _row_to_obj(cls, row: aiosqlite.Row) -> History:
        return History(
            id=uuid.UUID(row["id"]),
            message_data=json.loads(row["message_data"]),
            user_id=uuid.UUID(row["user_id"]),
            created_ts=row["created_ts"],
        )

    @classmethod
    def _obj_to_row(cls, data: History) -> dict[str, Any]:
        return {
            "id": str(data.id),
            "message_data": json.dumps(data.message_data),
            "user_id": str(data.user_id),
            "created_ts": data.created_ts,
        }


class LifeAreasManager(ORMBase[LifeArea]):
    _table = "life_areas"
    _columns = ("id", "title", "parent_id", "user_id", "extracted_at", "covered_at")
    _user_column = "user_id"

    @classmethod
    def _row_to_obj(cls, row: aiosqlite.Row) -> LifeArea:
        parent_id = row["parent_id"]
        extracted_at = row["extracted_at"]
        covered_at = row["covered_at"]
        return LifeArea(
            id=uuid.UUID(row["id"]),
            title=row["title"],
            parent_id=uuid.UUID(parent_id) if parent_id else None,
            user_id=uuid.UUID(row["user_id"]),
            extracted_at=extracted_at,
            covered_at=covered_at,
        )

    @classmethod
    def _obj_to_row(cls, data: LifeArea) -> dict[str, Any]:
        return {
            "id": str(data.id),
            "title": data.title,
            "parent_id": str(data.parent_id) if data.parent_id else None,
            "user_id": str(data.user_id),
            "extracted_at": data.extracted_at,
            "covered_at": data.covered_at,
        }

    @classmethod
    async def mark_extracted(
        cls,
        area_id: uuid.UUID,
        conn: aiosqlite.Connection | None = None,
        timestamp: float | None = None,
    ) -> None:
        """Mark area as extracted with given or current timestamp."""
        from src.shared.timestamp import get_timestamp

        from .connection import get_connection

        ts = timestamp if timestamp is not None else get_timestamp()
        query = f"UPDATE {cls._table} SET extracted_at = ? WHERE id = ?"
        if conn is None:
            async with get_connection() as local_conn:
                await local_conn.execute(query, (ts, str(area_id)))
                await local_conn.commit()
        else:
            await conn.execute(query, (ts, str(area_id)))

    @classmethod
    async def reset_extraction(
        cls, area_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> None:
        """Clear extracted_at to allow re-extraction."""
        from .connection import get_connection

        query = f"UPDATE {cls._table} SET extracted_at = NULL WHERE id = ?"
        if conn is None:
            async with get_connection() as local_conn:
                await local_conn.execute(query, (str(area_id),))
                await local_conn.commit()
        else:
            await conn.execute(query, (str(area_id),))

    @classmethod
    async def set_covered_at(
        cls,
        area_id: uuid.UUID,
        timestamp: float | None,
        conn: aiosqlite.Connection | None = None,
    ) -> None:
        """Set covered_at timestamp for a leaf area (NULL to reset)."""
        from .connection import get_connection

        query = f"UPDATE {cls._table} SET covered_at = ? WHERE id = ?"
        if conn is None:
            async with get_connection() as local_conn:
                await local_conn.execute(query, (timestamp, str(area_id)))
                await local_conn.commit()
        else:
            await conn.execute(query, (timestamp, str(area_id)))

    @classmethod
    async def get_descendants(
        cls, area_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> list[LifeArea]:
        """Get all descendant areas recursively using CTE."""
        from .connection import get_connection

        query = """
            WITH RECURSIVE descendants AS (
                SELECT id, title, parent_id, user_id, extracted_at, covered_at
                FROM life_areas
                WHERE parent_id = ?
                UNION ALL
                SELECT la.id, la.title, la.parent_id, la.user_id, la.extracted_at, la.covered_at
                FROM life_areas la
                JOIN descendants d ON la.parent_id = d.id
            )
            SELECT id, title, parent_id, user_id, extracted_at, covered_at FROM descendants
            ORDER BY id
        """
        if conn is None:
            async with get_connection() as local_conn:
                cursor = await local_conn.execute(query, (str(area_id),))
                rows = await cursor.fetchall()
        else:
            cursor = await conn.execute(query, (str(area_id),))
            rows = await cursor.fetchall()
        return [cls._row_to_obj(row) for row in rows]

    @classmethod
    async def get_ancestors(
        cls, area_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> list[LifeArea]:
        """Get all ancestor areas recursively using CTE (parent chain to root)."""
        from .connection import get_connection

        query = """
            WITH RECURSIVE ancestors AS (
                SELECT id, title, parent_id, user_id, extracted_at, covered_at
                FROM life_areas
                WHERE id = (SELECT parent_id FROM life_areas WHERE id = ?)
                UNION ALL
                SELECT la.id, la.title, la.parent_id, la.user_id, la.extracted_at, la.covered_at
                FROM life_areas la
                JOIN ancestors a ON la.id = a.parent_id
            )
            SELECT id, title, parent_id, user_id, extracted_at, covered_at FROM ancestors
        """
        if conn is None:
            async with get_connection() as local_conn:
                cursor = await local_conn.execute(query, (str(area_id),))
                rows = await cursor.fetchall()
        else:
            cursor = await conn.execute(query, (str(area_id),))
            rows = await cursor.fetchall()
        return [cls._row_to_obj(row) for row in rows]

    @classmethod
    async def would_create_cycle(
        cls,
        area_id: uuid.UUID,
        new_parent_id: uuid.UUID,
        conn: aiosqlite.Connection | None = None,
    ) -> bool:
        """Check if setting new_parent_id would create a cycle.

        A cycle occurs if new_parent_id is a descendant of area_id.
        Used for validating parent changes on update operations.
        """
        if area_id == new_parent_id:
            return True
        descendants = await cls.get_descendants(area_id, conn=conn)
        return any(d.id == new_parent_id for d in descendants)
