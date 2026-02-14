"""Interview-specific database managers."""

import json
import uuid
from typing import Any

import aiosqlite

from .base import ORMBase, _with_conn
from .models import ActiveInterviewContext, LeafCoverage


class LeafCoverageManager(ORMBase[LeafCoverage]):
    """Manager for leaf_coverage table."""

    _table = "leaf_coverage"
    _columns = (
        "leaf_id",
        "root_area_id",
        "status",
        "summary_text",
        "vector",
        "updated_at",
    )

    @classmethod
    def _row_to_obj(cls, row: aiosqlite.Row) -> LeafCoverage:
        vector = json.loads(row["vector"]) if row["vector"] else None
        return LeafCoverage(
            leaf_id=uuid.UUID(row["leaf_id"]),
            root_area_id=uuid.UUID(row["root_area_id"]),
            status=row["status"],
            summary_text=row["summary_text"],
            vector=vector,
            updated_at=row["updated_at"],
        )

    @classmethod
    def _obj_to_row(cls, data: LeafCoverage) -> dict[str, Any]:
        return {
            "leaf_id": str(data.leaf_id),
            "root_area_id": str(data.root_area_id),
            "status": data.status,
            "summary_text": data.summary_text,
            "vector": json.dumps(data.vector) if data.vector else None,
            "updated_at": data.updated_at,
        }

    @classmethod
    async def create(
        cls,
        leaf_id: uuid.UUID,
        data: LeafCoverage,
        conn: aiosqlite.Connection | None = None,
        auto_commit: bool = True,
    ):
        """Create a leaf coverage record if not exists. Uses leaf_id as primary key.

        Uses INSERT OR IGNORE to avoid race conditions when concurrent requests
        attempt to create the same record - the first write wins and subsequent
        attempts are safely ignored without overwriting existing data.
        """
        values = cls._obj_to_row(data)
        columns = ", ".join(values.keys())
        placeholders = ", ".join(["?"] * len(values))
        query = (
            f"INSERT OR IGNORE INTO {cls._table} ({columns}) VALUES ({placeholders})"
        )
        async with _with_conn(conn) as c:
            await c.execute(query, tuple(values.values()))
            if conn is None and auto_commit:
                await c.commit()

    @classmethod
    async def get_by_id(
        cls, leaf_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> LeafCoverage | None:
        """Retrieve leaf coverage by leaf_id (primary key)."""
        query = f"SELECT {', '.join(cls._columns)} FROM {cls._table} WHERE leaf_id = ?"
        async with _with_conn(conn) as c:
            cursor = await c.execute(query, (str(leaf_id),))
            row = await cursor.fetchone()
        return cls._row_to_obj(row) if row else None

    @classmethod
    async def list_by_root_area(
        cls, root_area_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> list[LeafCoverage]:
        """List all leaf coverage records for a root area.

        Results are ordered by updated_at to ensure deterministic leaf selection
        when iterating through uncovered leaves.
        """
        return await cls._list_by_column(
            "root_area_id", str(root_area_id), conn, order_by="updated_at"
        )

    @classmethod
    async def update_status(
        cls,
        leaf_id: uuid.UUID,
        status: str,
        updated_at: float,
        conn: aiosqlite.Connection | None = None,
    ):
        """Update the status of a leaf coverage record."""
        query = f"UPDATE {cls._table} SET status = ?, updated_at = ? WHERE leaf_id = ?"
        async with _with_conn(conn) as c:
            await c.execute(query, (status, updated_at, str(leaf_id)))
            if conn is None:
                await c.commit()

    @classmethod
    async def save_summary(
        cls,
        leaf_id: uuid.UUID,
        summary_text: str,
        vector: list[float],
        updated_at: float,
        conn: aiosqlite.Connection | None = None,
    ):
        """Save summary and vector for a covered leaf."""
        query = f"UPDATE {cls._table} SET summary_text=?, vector=?, updated_at=? WHERE leaf_id=?"
        async with _with_conn(conn) as c:
            await c.execute(
                query, (summary_text, json.dumps(vector), updated_at, str(leaf_id))
            )
            if conn is None:
                await c.commit()

    @classmethod
    async def delete_by_root_area(
        cls, root_area_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> None:
        """Delete all leaf coverage records for a root area."""
        query = f"DELETE FROM {cls._table} WHERE root_area_id = ?"
        async with _with_conn(conn) as c:
            await c.execute(query, (str(root_area_id),))
            if conn is None:
                await c.commit()


class ActiveInterviewContextManager(ORMBase[ActiveInterviewContext]):
    """Manager for active_interview_context table."""

    _table = "active_interview_context"
    _columns = (
        "user_id",
        "root_area_id",
        "active_leaf_id",
        "question_text",
        "created_at",
    )

    @classmethod
    def _row_to_obj(cls, row: aiosqlite.Row) -> ActiveInterviewContext:
        return ActiveInterviewContext(
            user_id=uuid.UUID(row["user_id"]),
            root_area_id=uuid.UUID(row["root_area_id"]),
            active_leaf_id=uuid.UUID(row["active_leaf_id"]),
            question_text=row["question_text"],
            created_at=row["created_at"],
        )

    @classmethod
    def _obj_to_row(cls, data: ActiveInterviewContext) -> dict[str, Any]:
        return {
            "user_id": str(data.user_id),
            "root_area_id": str(data.root_area_id),
            "active_leaf_id": str(data.active_leaf_id),
            "question_text": data.question_text,
            "created_at": data.created_at,
        }

    @classmethod
    async def create(
        cls,
        user_id: uuid.UUID,
        data: ActiveInterviewContext,
        conn: aiosqlite.Connection | None = None,
        auto_commit: bool = True,
    ):
        """Create an active interview context. Uses user_id as primary key (no id column)."""
        values = cls._obj_to_row(data)
        columns = ", ".join(values.keys())
        placeholders = ", ".join(["?"] * len(values))
        query = (
            f"INSERT OR REPLACE INTO {cls._table} ({columns}) VALUES ({placeholders})"
        )
        async with _with_conn(conn) as c:
            await c.execute(query, tuple(values.values()))
            if conn is None and auto_commit:
                await c.commit()

    @classmethod
    async def get_by_user(
        cls, user_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> ActiveInterviewContext | None:
        """Retrieve active context for a user."""
        query = f"SELECT {', '.join(cls._columns)} FROM {cls._table} WHERE user_id = ?"
        async with _with_conn(conn) as c:
            cursor = await c.execute(query, (str(user_id),))
            row = await cursor.fetchone()
        return cls._row_to_obj(row) if row else None

    @classmethod
    async def update_active_leaf(
        cls,
        user_id: uuid.UUID,
        active_leaf_id: uuid.UUID,
        question_text: str | None,
        conn: aiosqlite.Connection | None = None,
    ):
        """Update the active leaf."""
        query = (
            f"UPDATE {cls._table} SET active_leaf_id=?, question_text=? WHERE user_id=?"
        )
        async with _with_conn(conn) as c:
            await c.execute(query, (str(active_leaf_id), question_text, str(user_id)))
            if conn is None:
                await c.commit()

    @classmethod
    async def delete_by_user(
        cls, user_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ):
        """Delete active context for a user."""
        query = f"DELETE FROM {cls._table} WHERE user_id = ?"
        async with _with_conn(conn) as c:
            await c.execute(query, (str(user_id),))
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
