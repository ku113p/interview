"""Knowledge repository managers: UserKnowledge."""

import uuid
from typing import Any

import aiosqlite

from .base import ORMBase, _with_conn
from .models import UserKnowledge


class UserKnowledgeManager(ORMBase[UserKnowledge]):
    _table = "user_knowledge"
    _columns = ("id", "description", "kind", "confidence", "created_ts", "summary_id")

    @classmethod
    def _row_to_obj(cls, row: aiosqlite.Row) -> UserKnowledge:
        summary_id = row["summary_id"]
        return UserKnowledge(
            id=uuid.UUID(row["id"]),
            description=row["description"],
            kind=row["kind"],
            confidence=row["confidence"],
            created_ts=row["created_ts"],
            summary_id=uuid.UUID(summary_id) if summary_id else None,
        )

    @classmethod
    def _obj_to_row(cls, data: UserKnowledge) -> dict[str, Any]:
        return {
            "id": str(data.id),
            "description": data.description,
            "kind": data.kind,
            "confidence": data.confidence,
            "created_ts": data.created_ts,
            "summary_id": str(data.summary_id) if data.summary_id else None,
        }

    @classmethod
    async def list_by_user(
        cls, user_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> list[UserKnowledge]:
        """List knowledge items for a user via summary → life_areas join."""
        query = """
            SELECT uk.id, uk.description, uk.kind, uk.confidence,
                   uk.created_ts, uk.summary_id
            FROM user_knowledge uk
            JOIN summaries s ON uk.summary_id = s.id
            JOIN life_areas la ON s.area_id = la.id
            WHERE la.user_id = ?
        """
        async with _with_conn(conn) as c:
            cursor = await c.execute(query, (str(user_id),))
            rows = await cursor.fetchall()
        return [cls._row_to_obj(row) for row in rows]
