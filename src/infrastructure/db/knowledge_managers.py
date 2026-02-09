"""Knowledge repository managers: UserKnowledge, UserKnowledgeAreas."""

import uuid
from typing import Any

import aiosqlite

from .base import ORMBase
from .models import UserKnowledge, UserKnowledgeArea


class UserKnowledgeManager(ORMBase[UserKnowledge]):
    _table = "user_knowledge"
    _columns = ("id", "description", "kind", "confidence", "created_ts")

    @classmethod
    def _row_to_obj(cls, row: aiosqlite.Row) -> UserKnowledge:
        return UserKnowledge(
            id=uuid.UUID(row["id"]),
            description=row["description"],
            kind=row["kind"],
            confidence=row["confidence"],
            created_ts=row["created_ts"],
        )

    @classmethod
    def _obj_to_row(cls, data: UserKnowledge) -> dict[str, Any]:
        return {
            "id": str(data.id),
            "description": data.description,
            "kind": data.kind,
            "confidence": data.confidence,
            "created_ts": data.created_ts,
        }


class UserKnowledgeAreasManager:
    """Manager for the user_knowledge_areas link table."""

    _table = "user_knowledge_areas"

    @classmethod
    async def create_link(
        cls,
        data: UserKnowledgeArea,
        conn: aiosqlite.Connection | None = None,
        auto_commit: bool = True,
    ):
        """Create a link between user, knowledge, and area."""
        from src.infrastructure.db.connection import get_connection

        query = f"""
            INSERT OR REPLACE INTO {cls._table}
            (user_id, knowledge_id, area_id)
            VALUES (?, ?, ?)
        """
        values = (str(data.user_id), str(data.knowledge_id), str(data.area_id))

        if conn is None:
            async with get_connection() as local_conn:
                await local_conn.execute(query, values)
                if auto_commit:
                    await local_conn.commit()
        else:
            await conn.execute(query, values)

    @classmethod
    async def list_by_user(
        cls, user_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> list[UserKnowledgeArea]:
        """List all knowledge links for a user."""
        from src.infrastructure.db.connection import get_connection

        query = f"""
            SELECT user_id, knowledge_id, area_id
            FROM {cls._table}
            WHERE user_id = ?
        """
        if conn is None:
            async with get_connection() as local_conn:
                cursor = await local_conn.execute(query, (str(user_id),))
                rows = await cursor.fetchall()
        else:
            cursor = await conn.execute(query, (str(user_id),))
            rows = await cursor.fetchall()

        return [
            UserKnowledgeArea(
                user_id=uuid.UUID(row["user_id"]),
                knowledge_id=uuid.UUID(row["knowledge_id"]),
                area_id=uuid.UUID(row["area_id"]),
            )
            for row in rows
        ]

    @classmethod
    async def list_by_area(
        cls, area_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> list[UserKnowledgeArea]:
        """List all knowledge links for an area."""
        from src.infrastructure.db.connection import get_connection

        query = f"""
            SELECT user_id, knowledge_id, area_id
            FROM {cls._table}
            WHERE area_id = ?
        """
        if conn is None:
            async with get_connection() as local_conn:
                cursor = await local_conn.execute(query, (str(area_id),))
                rows = await cursor.fetchall()
        else:
            cursor = await conn.execute(query, (str(area_id),))
            rows = await cursor.fetchall()

        return [
            UserKnowledgeArea(
                user_id=uuid.UUID(row["user_id"]),
                knowledge_id=uuid.UUID(row["knowledge_id"]),
                area_id=uuid.UUID(row["area_id"]),
            )
            for row in rows
        ]

    @classmethod
    async def delete_link(
        cls,
        user_id: uuid.UUID,
        knowledge_id: uuid.UUID,
        conn: aiosqlite.Connection | None = None,
        auto_commit: bool = True,
    ):
        """Delete a specific knowledge link."""
        from src.infrastructure.db.connection import get_connection

        query = f"""
            DELETE FROM {cls._table}
            WHERE user_id = ? AND knowledge_id = ?
        """
        if conn is None:
            async with get_connection() as local_conn:
                await local_conn.execute(query, (str(user_id), str(knowledge_id)))
                if auto_commit:
                    await local_conn.commit()
        else:
            await conn.execute(query, (str(user_id), str(knowledge_id)))
