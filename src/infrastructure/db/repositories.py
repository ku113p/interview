import json
import sqlite3
import uuid
from dataclasses import dataclass
from typing import Any, Generic, Protocol, TypeVar, cast

# Define a TypeVar that represents our Data Objects
T = TypeVar("T")


class _ColumnFilterable(Protocol[T]):
    @classmethod
    def _list_by_column(
        cls,
        column: str,
        value: str,
        conn: sqlite3.Connection | None = None,
        order_by: str | None = None,
    ) -> list[T]: ...


class BaseModel(Generic[T]):
    """Generic base class for ORM models with common CRUD operations."""

    _table: str
    _columns: tuple[str, ...]

    @classmethod
    def _row_to_obj(cls, row: sqlite3.Row) -> T:
        """Convert database row to domain object. Must be implemented by subclasses."""
        raise NotImplementedError

    @classmethod
    def _obj_to_row(cls, data: T) -> dict[str, Any]:
        """Convert domain object to database row. Must be implemented by subclasses."""
        raise NotImplementedError

    @classmethod
    def _list_by_column(
        cls,
        column: str,
        value: str,
        conn: sqlite3.Connection | None = None,
        order_by: str | None = None,
    ) -> list[T]:
        """Query objects by a specific column value."""
        from src.infrastructure.db.connection import get_connection

        query = f"SELECT {', '.join(cls._columns)} FROM {cls._table} WHERE {column} = ?"
        if order_by is not None:
            query = f"{query} ORDER BY {order_by}"
        if conn is None:
            with get_connection() as local_conn:
                rows = local_conn.execute(query, (value,)).fetchall()
        else:
            rows = conn.execute(query, (value,)).fetchall()
        return [cls._row_to_obj(row) for row in rows]

    @classmethod
    def get_by_id(
        cls, id: uuid.UUID, conn: sqlite3.Connection | None = None
    ) -> T | None:
        """Retrieve a single object by ID."""
        from src.infrastructure.db.connection import get_connection

        query = f"SELECT {', '.join(cls._columns)} FROM {cls._table} WHERE id = ?"
        if conn is None:
            with get_connection() as local_conn:
                row = local_conn.execute(query, (str(id),)).fetchone()
        else:
            row = conn.execute(query, (str(id),)).fetchone()
        if row is None:
            return None
        return cls._row_to_obj(row)

    @classmethod
    def list(cls, conn: sqlite3.Connection | None = None) -> list[T]:
        """Retrieve all objects from the table."""
        from src.infrastructure.db.connection import get_connection

        query = f"SELECT {', '.join(cls._columns)} FROM {cls._table}"
        if conn is None:
            with get_connection() as local_conn:
                rows = local_conn.execute(query).fetchall()
        else:
            rows = conn.execute(query).fetchall()
        return [cls._row_to_obj(row) for row in rows]

    @classmethod
    def create(
        cls,
        id: uuid.UUID,
        data: T,
        conn: sqlite3.Connection | None = None,
    ):
        """Create or replace an object in the database."""
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
            with get_connection() as local_conn:
                local_conn.execute(query, tuple(values.values()))
                local_conn.commit()
        else:
            conn.execute(query, tuple(values.values()))

    @classmethod
    def update(
        cls,
        id: uuid.UUID,
        data: T,
        conn: sqlite3.Connection | None = None,
    ):
        """Update an object (uses create for simplicity)."""
        cls.create(id, data, conn=conn)

    @classmethod
    def delete(cls, id: uuid.UUID, conn: sqlite3.Connection | None = None):
        """Delete an object by ID."""
        from src.infrastructure.db.connection import get_connection

        query = f"DELETE FROM {cls._table} WHERE id = ?"
        if conn is None:
            with get_connection() as local_conn:
                local_conn.execute(query, (str(id),))
                local_conn.commit()
        else:
            conn.execute(query, (str(id),))


class UserFilterMixin(Generic[T]):
    """Mixin for models that support filtering by user_id."""

    @classmethod
    def list_by_user(
        cls, user_id: uuid.UUID, conn: sqlite3.Connection | None = None
    ) -> list[T]:
        model = cast(_ColumnFilterable[T], cls)
        return model._list_by_column("user_id", str(user_id), conn)


class AreaFilterMixin(Generic[T]):
    """Mixin for models that support filtering by area_id."""

    @classmethod
    def list_by_area(
        cls, area_id: uuid.UUID, conn: sqlite3.Connection | None = None
    ) -> list[T]:
        model = cast(_ColumnFilterable[T], cls)
        return model._list_by_column("area_id", str(area_id), conn)


# Domain Models


@dataclass
class User:
    id: uuid.UUID
    name: str
    mode: str
    current_area_id: uuid.UUID | None = None


@dataclass(frozen=True)
class History:
    id: uuid.UUID
    data: dict
    user_id: uuid.UUID
    created_ts: float


@dataclass
class LifeArea:
    id: uuid.UUID
    title: str
    parent_id: uuid.UUID | None
    user_id: uuid.UUID


@dataclass
class Criteria:
    id: uuid.UUID
    title: str
    area_id: uuid.UUID


@dataclass
class LifeAreaMessage:
    id: uuid.UUID
    data: str
    area_id: uuid.UUID
    created_ts: float


# Repository Managers


class UsersManager(BaseModel[User]):
    _table = "users"
    _columns = ("id", "name", "mode", "current_area_id")

    @classmethod
    def _row_to_obj(cls, row: sqlite3.Row) -> User:
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


class HistoryManager(BaseModel[History], UserFilterMixin[History]):
    _table = "histories"
    _columns = ("id", "data", "user_id", "created_ts")

    @classmethod
    def _row_to_obj(cls, row: sqlite3.Row) -> History:
        return History(
            id=uuid.UUID(row["id"]),
            data=json.loads(row["data"]),
            user_id=uuid.UUID(row["user_id"]),
            created_ts=row["created_ts"],
        )

    @classmethod
    def _obj_to_row(cls, data: History) -> dict[str, Any]:
        return {
            "id": str(data.id),
            "data": json.dumps(data.data),
            "user_id": str(data.user_id),
            "created_ts": data.created_ts,
        }


class LifeAreaManager(BaseModel[LifeArea], UserFilterMixin[LifeArea]):
    _table = "life_areas"
    _columns = ("id", "title", "parent_id", "user_id")

    @classmethod
    def _row_to_obj(cls, row: sqlite3.Row) -> LifeArea:
        parent_id = row["parent_id"]
        return LifeArea(
            id=uuid.UUID(row["id"]),
            title=row["title"],
            parent_id=uuid.UUID(parent_id) if parent_id else None,
            user_id=uuid.UUID(row["user_id"]),
        )

    @classmethod
    def _obj_to_row(cls, data: LifeArea) -> dict[str, Any]:
        return {
            "id": str(data.id),
            "title": data.title,
            "parent_id": str(data.parent_id) if data.parent_id else None,
            "user_id": str(data.user_id),
        }


class CriteriaManager(BaseModel[Criteria], AreaFilterMixin[Criteria]):
    _table = "criteria"
    _columns = ("id", "title", "area_id")

    @classmethod
    def _row_to_obj(cls, row: sqlite3.Row) -> Criteria:
        return Criteria(
            id=uuid.UUID(row["id"]),
            title=row["title"],
            area_id=uuid.UUID(row["area_id"]),
        )

    @classmethod
    def _obj_to_row(cls, data: Criteria) -> dict[str, Any]:
        return {
            "id": str(data.id),
            "title": data.title,
            "area_id": str(data.area_id),
        }


class LifeAreaMessagesManager(
    BaseModel[LifeAreaMessage], AreaFilterMixin[LifeAreaMessage]
):
    _table = "life_area_messages"
    _columns = ("id", "data", "area_id", "created_ts")

    @classmethod
    def list_by_area(
        cls, area_id: uuid.UUID, conn: sqlite3.Connection | None = None
    ) -> list[LifeAreaMessage]:
        return cls._list_by_column(
            "area_id",
            str(area_id),
            conn,
            order_by="created_ts",
        )

    @classmethod
    def _row_to_obj(cls, row: sqlite3.Row) -> LifeAreaMessage:
        return LifeAreaMessage(
            id=uuid.UUID(row["id"]),
            data=row["data"],
            area_id=uuid.UUID(row["area_id"]),
            created_ts=row["created_ts"],
        )

    @classmethod
    def _obj_to_row(cls, data: LifeAreaMessage) -> dict[str, Any]:
        return {
            "id": str(data.id),
            "data": data.data,
            "area_id": str(data.area_id),
            "created_ts": data.created_ts,
        }
