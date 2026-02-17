"""Interview-specific database managers."""

import json
import uuid
from typing import Any

import aiosqlite

from .base import ORMBase, _with_conn
from .models import Summary


class SummariesManager(ORMBase[Summary]):
    """Manager for summaries table (per-turn summaries for leaf areas)."""

    _table = "summaries"
    _columns = (
        "id",
        "area_id",
        "summary_text",
        "question_id",
        "answer_id",
        "vector",
        "created_at",
    )
    _area_column = "area_id"

    @classmethod
    def _row_to_obj(cls, row: aiosqlite.Row) -> Summary:
        vector = json.loads(row["vector"]) if row["vector"] else None
        return Summary(
            id=uuid.UUID(row["id"]),
            area_id=uuid.UUID(row["area_id"]),
            summary_text=row["summary_text"],
            question_id=uuid.UUID(row["question_id"]) if row["question_id"] else None,
            answer_id=uuid.UUID(row["answer_id"]) if row["answer_id"] else None,
            vector=vector,
            created_at=row["created_at"],
        )

    @classmethod
    def _obj_to_row(cls, data: Summary) -> dict[str, Any]:
        return {
            "id": str(data.id),
            "area_id": str(data.area_id),
            "summary_text": data.summary_text,
            "question_id": str(data.question_id) if data.question_id else None,
            "answer_id": str(data.answer_id) if data.answer_id else None,
            "vector": json.dumps(data.vector) if data.vector else None,
            "created_at": data.created_at,
        }

    @classmethod
    async def create_summary(
        cls,
        area_id: uuid.UUID,
        summary_text: str,
        created_at: float,
        question_id: uuid.UUID | None = None,
        answer_id: uuid.UUID | None = None,
        conn: aiosqlite.Connection | None = None,
    ) -> uuid.UUID:
        """Create a new summary record and return its id."""
        from src.shared.ids import new_id

        summary_id = new_id()
        summary = Summary(
            id=summary_id,
            area_id=area_id,
            summary_text=summary_text,
            created_at=created_at,
            question_id=question_id,
            answer_id=answer_id,
        )
        await cls.create(summary_id, summary, conn=conn, auto_commit=(conn is None))
        return summary_id

    @classmethod
    async def list_by_area(
        cls, area_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> list[Summary]:
        """List all summaries for a leaf area, ordered by creation time."""
        return await cls._list_by_column(
            "area_id", str(area_id), conn, order_by="created_at"
        )

    @classmethod
    async def update_vector(
        cls,
        summary_id: uuid.UUID,
        vector: list[float],
        conn: aiosqlite.Connection | None = None,
    ) -> None:
        """Write embedding vector to a summary record."""
        query = f"UPDATE {cls._table} SET vector = ? WHERE id = ?"
        async with _with_conn(conn) as c:
            await c.execute(query, (json.dumps(vector), str(summary_id)))
            if conn is None:
                await c.commit()

    @classmethod
    async def delete_by_area(
        cls, area_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> None:
        """Delete all summaries for a leaf area."""
        query = f"DELETE FROM {cls._table} WHERE area_id = ?"
        async with _with_conn(conn) as c:
            await c.execute(query, (str(area_id),))
            if conn is None:
                await c.commit()


class LeafHistoryManager:
    """Manager for leaf_history join table.

    Note: Does not extend ORMBase because this is a pure join table
    without a corresponding model class - it only links leaf_id to history_id.
    """

    _table = "leaf_history"

    @classmethod
    async def link(
        cls,
        leaf_id: uuid.UUID,
        history_id: uuid.UUID,
        conn: aiosqlite.Connection | None = None,
    ) -> None:
        """Link a history message to a leaf."""
        query = (
            f"INSERT OR IGNORE INTO {cls._table} (leaf_id, history_id) VALUES (?, ?)"
        )
        async with _with_conn(conn) as c:
            await c.execute(query, (str(leaf_id), str(history_id)))
            if conn is None:
                await c.commit()

    @classmethod
    async def get_messages(
        cls, leaf_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> list[dict]:
        """Get all history messages for a leaf, ordered by time.

        Returns:
            List of message_data dicts (role, content) in chronological order.
        """
        query = """
            SELECT h.message_data, h.created_ts
            FROM leaf_history lh
            JOIN histories h ON lh.history_id = h.id
            WHERE lh.leaf_id = ?
            ORDER BY h.created_ts
        """
        async with _with_conn(conn) as c:
            cursor = await c.execute(query, (str(leaf_id),))
            rows = await cursor.fetchall()
        return [json.loads(row["message_data"]) for row in rows]

    @classmethod
    async def get_messages_with_ids(
        cls, leaf_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> list[tuple[uuid.UUID, dict]]:
        """Get all history messages for a leaf with their IDs, ordered by time.

        Returns:
            List of (history_id, message_data) pairs in chronological order.
        """
        query = """
            SELECT h.id, h.message_data
            FROM histories h
            JOIN leaf_history lh ON h.id = lh.history_id
            WHERE lh.leaf_id = ?
            ORDER BY h.created_ts
        """
        async with _with_conn(conn) as c:
            cursor = await c.execute(query, (str(leaf_id),))
            rows = await cursor.fetchall()
        return [(uuid.UUID(row["id"]), json.loads(row["message_data"])) for row in rows]

    @classmethod
    async def get_message_count(
        cls, leaf_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> int:
        """Get count of messages linked to a leaf."""
        query = f"SELECT COUNT(*) FROM {cls._table} WHERE leaf_id = ?"
        async with _with_conn(conn) as c:
            cursor = await c.execute(query, (str(leaf_id),))
            row = await cursor.fetchone()
        return row[0] if row else 0

    @classmethod
    async def delete_by_leaf(
        cls, leaf_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> None:
        """Delete all history links for a leaf."""
        query = f"DELETE FROM {cls._table} WHERE leaf_id = ?"
        async with _with_conn(conn) as c:
            await c.execute(query, (str(leaf_id),))
            if conn is None:
                await c.commit()
