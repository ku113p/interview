"""API key database manager."""

import hashlib
import uuid
from typing import Any

import aiosqlite

from .base import ORMBase, _with_conn
from .models import ApiKey


def hash_key(key: str) -> str:
    """Return the SHA-256 hex digest of an API key."""
    return hashlib.sha256(key.encode()).hexdigest()


class ApiKeysManager(ORMBase[ApiKey]):
    _table = "api_keys"
    _columns = ("id", "key_hash", "key_prefix", "user_id", "label", "created_at")
    _user_column = "user_id"

    @classmethod
    def _row_to_obj(cls, row: aiosqlite.Row) -> ApiKey:
        return ApiKey(
            id=uuid.UUID(row["id"]),
            key_hash=row["key_hash"],
            key_prefix=row["key_prefix"],
            user_id=uuid.UUID(row["user_id"]),
            label=row["label"],
            created_at=row["created_at"],
        )

    @classmethod
    def _obj_to_row(cls, data: ApiKey) -> dict[str, Any]:
        return {
            "id": str(data.id),
            "key_hash": data.key_hash,
            "key_prefix": data.key_prefix,
            "user_id": str(data.user_id),
            "label": data.label,
            "created_at": data.created_at,
        }

    @classmethod
    async def get_by_key(
        cls, key: str, conn: aiosqlite.Connection | None = None
    ) -> ApiKey | None:
        """Look up an API key by its raw key string (hashed for lookup)."""
        query = f"SELECT {', '.join(cls._columns)} FROM {cls._table} WHERE key_hash = ?"
        async with _with_conn(conn) as c:
            cursor = await c.execute(query, (hash_key(key),))
            row = await cursor.fetchone()
        if row is None:
            return None
        return cls._row_to_obj(row)
