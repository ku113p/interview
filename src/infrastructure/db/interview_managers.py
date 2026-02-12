"""Interview-specific database managers."""

import json
import uuid
from typing import Any

import aiosqlite

from .base import ORMBase, _with_conn
from .connection import transaction
from .models import ActiveInterviewContext, LeafCoverage, LeafExtractionQueueItem


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
        """Create a leaf coverage record. Uses leaf_id as primary key (no id column)."""
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
        """List all leaf coverage records for a root area."""
        return await cls._list_by_column("root_area_id", str(root_area_id), conn)

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


class ActiveInterviewContextManager(ORMBase[ActiveInterviewContext]):
    """Manager for active_interview_context table."""

    _table = "active_interview_context"
    _columns = (
        "user_id",
        "root_area_id",
        "active_leaf_id",
        "question_text",
        "message_ids",
        "created_at",
    )

    @classmethod
    def _row_to_obj(cls, row: aiosqlite.Row) -> ActiveInterviewContext:
        message_ids = json.loads(row["message_ids"]) if row["message_ids"] else None
        return ActiveInterviewContext(
            user_id=uuid.UUID(row["user_id"]),
            root_area_id=uuid.UUID(row["root_area_id"]),
            active_leaf_id=uuid.UUID(row["active_leaf_id"]),
            question_text=row["question_text"],
            message_ids=message_ids,
            created_at=row["created_at"],
        )

    @classmethod
    def _obj_to_row(cls, data: ActiveInterviewContext) -> dict[str, Any]:
        return {
            "user_id": str(data.user_id),
            "root_area_id": str(data.root_area_id),
            "active_leaf_id": str(data.active_leaf_id),
            "question_text": data.question_text,
            "message_ids": json.dumps(data.message_ids) if data.message_ids else None,
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
    async def update_message_ids(
        cls,
        user_id: uuid.UUID,
        message_ids: list[str],
        conn: aiosqlite.Connection | None = None,
    ):
        """Update the message_ids list for a user's active context."""
        query = f"UPDATE {cls._table} SET message_ids = ? WHERE user_id = ?"
        async with _with_conn(conn) as c:
            await c.execute(query, (json.dumps(message_ids), str(user_id)))
            if conn is None:
                await c.commit()

    @classmethod
    async def update_active_leaf(
        cls,
        user_id: uuid.UUID,
        active_leaf_id: uuid.UUID,
        question_text: str | None,
        conn: aiosqlite.Connection | None = None,
    ):
        """Update the active leaf and reset message_ids."""
        query = f"UPDATE {cls._table} SET active_leaf_id=?, question_text=?, message_ids=? WHERE user_id=?"
        async with _with_conn(conn) as c:
            await c.execute(
                query, (str(active_leaf_id), question_text, "[]", str(user_id))
            )
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


class LeafExtractionQueueManager(ORMBase[LeafExtractionQueueItem]):
    """Manager for leaf_extraction_queue table."""

    _table = "leaf_extraction_queue"
    _columns = (
        "id",
        "leaf_id",
        "root_area_id",
        "message_ids",
        "status",
        "retry_count",
        "created_at",
        "processed_at",
    )

    @classmethod
    def _row_to_obj(cls, row: aiosqlite.Row) -> LeafExtractionQueueItem:
        return LeafExtractionQueueItem(
            id=uuid.UUID(row["id"]),
            leaf_id=uuid.UUID(row["leaf_id"]),
            root_area_id=uuid.UUID(row["root_area_id"]),
            message_ids=json.loads(row["message_ids"]),
            status=row["status"],
            retry_count=row["retry_count"],
            created_at=row["created_at"],
            processed_at=row["processed_at"],
        )

    @classmethod
    def _obj_to_row(cls, data: LeafExtractionQueueItem) -> dict[str, Any]:
        return {
            "id": str(data.id),
            "leaf_id": str(data.leaf_id),
            "root_area_id": str(data.root_area_id),
            "message_ids": json.dumps(data.message_ids),
            "status": data.status,
            "retry_count": data.retry_count,
            "created_at": data.created_at,
            "processed_at": data.processed_at,
        }

    @classmethod
    async def claim_pending(
        cls, limit: int = 1, conn: aiosqlite.Connection | None = None
    ) -> list[LeafExtractionQueueItem]:
        """Atomically claim pending tasks for processing.

        Uses explicit transaction control to prevent race conditions between workers.
        """
        if conn is not None:
            return await cls._do_claim(limit, conn)

        async with transaction() as tx_conn:
            return await cls._do_claim(limit, tx_conn)

    @classmethod
    async def _do_claim(
        cls, limit: int, conn: aiosqlite.Connection
    ) -> list[LeafExtractionQueueItem]:
        """Internal: perform claim within a transaction."""
        select_query = f"""
            SELECT {', '.join(cls._columns)} FROM {cls._table}
            WHERE status='pending' ORDER BY created_at LIMIT ?
        """
        cursor = await conn.execute(select_query, (limit,))
        rows = await cursor.fetchall()
        if not rows:
            return []

        task_ids = [row["id"] for row in rows]
        placeholders = ",".join(["?"] * len(task_ids))
        update_query = (
            f"UPDATE {cls._table} SET status='processing' "
            f"WHERE id IN ({placeholders})"
        )
        await conn.execute(update_query, task_ids)
        # No commit - transaction() handles it

        return [cls._row_to_obj(row) for row in rows]

    @classmethod
    async def mark_completed(
        cls,
        task_id: uuid.UUID,
        processed_at: float,
        conn: aiosqlite.Connection | None = None,
    ):
        """Mark a task as completed."""
        query = f"UPDATE {cls._table} SET status='completed', processed_at=? WHERE id=?"
        async with _with_conn(conn) as c:
            await c.execute(query, (processed_at, str(task_id)))
            if conn is None:
                await c.commit()

    @classmethod
    async def mark_failed(
        cls, task_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ):
        """Mark a task as failed and increment retry count."""
        query = f"UPDATE {cls._table} SET status='failed', retry_count=retry_count+1 WHERE id=?"
        async with _with_conn(conn) as c:
            await c.execute(query, (str(task_id),))
            if conn is None:
                await c.commit()

    @classmethod
    async def requeue_failed(
        cls, max_retries: int = 3, conn: aiosqlite.Connection | None = None
    ):
        """Requeue failed tasks under max retries. Tasks at max stay failed for investigation."""
        query = f"UPDATE {cls._table} SET status='pending' WHERE status='failed' AND retry_count < ?"
        async with _with_conn(conn) as c:
            await c.execute(query, (max_retries,))
            if conn is None:
                await c.commit()
