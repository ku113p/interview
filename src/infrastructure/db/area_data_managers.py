"""Area data repository managers: LifeAreaMessages and AreaSummaries."""

import uuid
from typing import Any

import aiosqlite

from .base import ORMBase
from .models import AreaSummary, LifeAreaMessage


def _serialize_vector(vector: list[float]) -> bytes:
    """Serialize embedding vector to bytes for storage."""
    import struct

    return struct.pack(f"{len(vector)}f", *vector)


def _deserialize_vector(data: bytes) -> list[float]:
    """Deserialize bytes back to embedding vector."""
    import struct

    count = len(data) // 4  # float is 4 bytes
    return list(struct.unpack(f"{count}f", data))


class LifeAreaMessagesManager(ORMBase[LifeAreaMessage]):
    _table = "life_area_messages"
    _columns = ("id", "message_text", "area_id", "created_ts")
    _area_column = "area_id"

    @classmethod
    async def list_by_area(
        cls, area_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> list[LifeAreaMessage]:
        return await cls._list_by_column(
            "area_id",
            str(area_id),
            conn,
            order_by="created_ts",
        )

    @classmethod
    def _row_to_obj(cls, row: aiosqlite.Row) -> LifeAreaMessage:
        return LifeAreaMessage(
            id=uuid.UUID(row["id"]),
            message_text=row["message_text"],
            area_id=uuid.UUID(row["area_id"]),
            created_ts=row["created_ts"],
        )

    @classmethod
    def _obj_to_row(cls, data: LifeAreaMessage) -> dict[str, Any]:
        return {
            "id": str(data.id),
            "message_text": data.message_text,
            "area_id": str(data.area_id),
            "created_ts": data.created_ts,
        }


class AreaSummariesManager(ORMBase[AreaSummary]):
    _table = "area_summaries"
    _columns = ("id", "area_id", "summary_text", "vector", "created_ts")
    _area_column = "area_id"

    @classmethod
    async def list_by_area(
        cls, area_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> list[AreaSummary]:
        return await cls._list_by_column(
            "area_id",
            str(area_id),
            conn,
            order_by="created_ts DESC",
        )

    @classmethod
    async def get_latest_by_area(
        cls, area_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> AreaSummary | None:
        results = await cls.list_by_area(area_id, conn)
        return results[0] if results else None

    @classmethod
    def _row_to_obj(cls, row: aiosqlite.Row) -> AreaSummary:
        return AreaSummary(
            id=uuid.UUID(row["id"]),
            area_id=uuid.UUID(row["area_id"]),
            summary_text=row["summary_text"],
            vector=_deserialize_vector(row["vector"]),
            created_ts=row["created_ts"],
        )

    @classmethod
    def _obj_to_row(cls, data: AreaSummary) -> dict[str, Any]:
        return {
            "id": str(data.id),
            "area_id": str(data.area_id),
            "summary_text": data.summary_text,
            "vector": _serialize_vector(data.vector),
            "created_ts": data.created_ts,
        }
