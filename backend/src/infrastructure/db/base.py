"""Base ORM framework classes."""

import uuid
from contextlib import asynccontextmanager
from typing import Any, Generic, TypeVar

import aiosqlite

# Define a TypeVar that represents our Data Objects
T = TypeVar("T")


@asynccontextmanager
async def _with_conn(conn: aiosqlite.Connection | None):
    """Context manager that uses provided conn or creates a new one."""
    from src.infrastructure.db.connection import get_connection

    if conn is not None:
        yield conn
    else:
        async with get_connection() as local_conn:
            yield local_conn


class ORMBase(Generic[T]):
    """Generic base class for ORM models with common CRUD operations."""

    _table: str
    _columns: tuple[str, ...]
    _user_column: str | None = None  # Set to enable list_by_user
    _area_column: str | None = None  # Set to enable list_by_area

    @classmethod
    def _row_to_obj(cls, row: aiosqlite.Row) -> T:
        """Convert database row to domain object. Must be implemented by subclasses."""
        raise NotImplementedError

    @classmethod
    def _obj_to_row(cls, data: T) -> dict[str, Any]:
        """Convert domain object to database row. Must be implemented by subclasses."""
        raise NotImplementedError

    @classmethod
    async def _list_by_column(
        cls,
        column: str,
        value: str,
        conn: aiosqlite.Connection | None = None,
        order_by: str | None = None,
    ) -> list[T]:
        """Query objects by a specific column value."""
        from src.infrastructure.db.connection import get_connection

        query = f"SELECT {', '.join(cls._columns)} FROM {cls._table} WHERE {column} = ?"
        if order_by is not None:
            query = f"{query} ORDER BY {order_by}"
        if conn is None:
            async with get_connection() as local_conn:
                cursor = await local_conn.execute(query, (value,))
                rows = await cursor.fetchall()
        else:
            cursor = await conn.execute(query, (value,))
            rows = await cursor.fetchall()
        return [cls._row_to_obj(row) for row in rows]

    @classmethod
    async def list_by_user(
        cls, user_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> list[T]:
        """List objects by user_id. Requires _user_column to be set."""
        if cls._user_column is None:
            raise NotImplementedError(f"{cls.__name__} does not support list_by_user")
        return await cls._list_by_column(cls._user_column, str(user_id), conn)

    @classmethod
    async def list_by_area(
        cls, area_id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> list[T]:
        """List objects by area_id. Requires _area_column to be set."""
        if cls._area_column is None:
            raise NotImplementedError(f"{cls.__name__} does not support list_by_area")
        return await cls._list_by_column(cls._area_column, str(area_id), conn)

    @classmethod
    async def get_by_id(
        cls, id: uuid.UUID, conn: aiosqlite.Connection | None = None
    ) -> T | None:
        """Retrieve a single object by ID."""
        from src.infrastructure.db.connection import get_connection

        query = f"SELECT {', '.join(cls._columns)} FROM {cls._table} WHERE id = ?"
        if conn is None:
            async with get_connection() as local_conn:
                cursor = await local_conn.execute(query, (str(id),))
                row = await cursor.fetchone()
        else:
            cursor = await conn.execute(query, (str(id),))
            row = await cursor.fetchone()
        if row is None:
            return None
        return cls._row_to_obj(row)

    @classmethod
    async def get_by_ids(
        cls, ids: list[uuid.UUID], conn: aiosqlite.Connection | None = None
    ) -> list[T]:
        """Retrieve multiple objects by IDs in a single batch query.

        Args:
            ids: List of UUIDs to retrieve.
            conn: Optional existing connection.

        Returns:
            List of objects in the same order as the input IDs.
            Missing IDs are silently skipped in the result.
        """
        from src.infrastructure.db.connection import get_connection

        if not ids:
            return []

        id_strs = [str(id_) for id_ in ids]
        placeholders = ", ".join(["?"] * len(id_strs))
        query = (
            f"SELECT {', '.join(cls._columns)} FROM {cls._table} "
            f"WHERE id IN ({placeholders})"
        )

        if conn is None:
            async with get_connection() as local_conn:
                cursor = await local_conn.execute(query, id_strs)
                rows = await cursor.fetchall()
        else:
            cursor = await conn.execute(query, id_strs)
            rows = await cursor.fetchall()

        # Build dict for O(1) lookup, return in input order
        result_dict = {row["id"]: cls._row_to_obj(row) for row in rows}
        return [result_dict[id_str] for id_str in id_strs if id_str in result_dict]

    @classmethod
    async def list(cls, conn: aiosqlite.Connection | None = None) -> list[T]:
        """Retrieve all objects from the table."""
        from src.infrastructure.db.connection import get_connection

        query = f"SELECT {', '.join(cls._columns)} FROM {cls._table}"
        if conn is None:
            async with get_connection() as local_conn:
                cursor = await local_conn.execute(query)
                rows = await cursor.fetchall()
        else:
            cursor = await conn.execute(query)
            rows = await cursor.fetchall()
        return [cls._row_to_obj(row) for row in rows]

    @classmethod
    async def create(
        cls,
        id: uuid.UUID,
        data: T,
        conn: aiosqlite.Connection | None = None,
        auto_commit: bool = True,
    ):
        """Create or replace an object in the database.

        Args:
            id: Unique identifier for the object
            data: Domain object to persist
            conn: Optional existing connection (uses transaction if provided)
            auto_commit: If True and conn is None, auto-commits. If False, caller manages commit.
        """
        from src.infrastructure.db.connection import get_connection

        values = cls._obj_to_row(data)
        if "id" not in values:
            values["id"] = str(id)
        columns = ", ".join(values.keys())
        placeholders = ", ".join(["?"] * len(values))
        query = (
            f"INSERT OR REPLACE INTO {cls._table} ({columns}) VALUES ({placeholders})"
        )
        if conn is None:
            async with get_connection() as local_conn:
                await local_conn.execute(query, tuple(values.values()))
                if auto_commit:
                    await local_conn.commit()
        else:
            await conn.execute(query, tuple(values.values()))

    @classmethod
    async def update(
        cls,
        id: uuid.UUID,
        data: T,
        conn: aiosqlite.Connection | None = None,
        auto_commit: bool = True,
    ):
        """Update an object (uses create for simplicity)."""
        await cls.create(id, data, conn=conn, auto_commit=auto_commit)

    @classmethod
    async def delete(
        cls,
        id: uuid.UUID,
        conn: aiosqlite.Connection | None = None,
        auto_commit: bool = True,
    ):
        """Delete an object by ID.

        Args:
            id: Unique identifier of object to delete
            conn: Optional existing connection (uses transaction if provided)
            auto_commit: If True and conn is None, auto-commits. If False, caller manages commit.
        """
        from src.infrastructure.db.connection import get_connection

        query = f"DELETE FROM {cls._table} WHERE id = ?"
        if conn is None:
            async with get_connection() as local_conn:
                await local_conn.execute(query, (str(id),))
                if auto_commit:
                    await local_conn.commit()
        else:
            await conn.execute(query, (str(id),))
