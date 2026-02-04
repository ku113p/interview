import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Generator, Generic, Protocol, TypeVar, cast

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
    _table: str
    _columns: tuple[str, ...]
    _db_initialized_path: str | None = None

    @classmethod
    def _get_db_path(cls) -> str:
        return os.environ.get("INTERVIEW_DB_PATH", "interview.db")

    @classmethod
    @contextmanager
    def _connect(cls) -> Generator[sqlite3.Connection, None, None]:
        db_path = cls._get_db_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        cls._init_db(conn, db_path)
        try:
            yield conn
        finally:
            conn.close()

    @classmethod
    def _init_db(cls, conn: sqlite3.Connection, db_path: str) -> None:
        if cls._db_initialized_path == db_path:
            return
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                mode TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS histories (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                user_id TEXT NOT NULL,
                created_ts REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS life_areas (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                parent_id TEXT,
                user_id TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS criteria (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                area_id TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS life_area_messages (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                area_id TEXT NOT NULL,
                created_ts REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS histories_user_id_idx
                ON histories(user_id);
            CREATE INDEX IF NOT EXISTS histories_created_ts_idx
                ON histories(created_ts);
            CREATE INDEX IF NOT EXISTS life_areas_user_id_idx
                ON life_areas(user_id);
            CREATE INDEX IF NOT EXISTS criteria_area_id_idx
                ON criteria(area_id);
            CREATE INDEX IF NOT EXISTS life_area_messages_area_id_idx
                ON life_area_messages(area_id);
            CREATE INDEX IF NOT EXISTS life_area_messages_created_ts_idx
                ON life_area_messages(created_ts);
            """
        )
        cls._ensure_column(
            conn,
            "life_area_messages",
            "created_ts",
            "created_ts REAL NOT NULL DEFAULT 0",
        )
        conn.commit()
        cls._db_initialized_path = db_path

    @classmethod
    def _ensure_column(
        cls, conn: sqlite3.Connection, table: str, column: str, definition: str
    ) -> None:
        columns = {
            row["name"]
            for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
        }
        if column in columns:
            return
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {definition}")

    @classmethod
    def _row_to_obj(cls, row: sqlite3.Row) -> T:
        raise NotImplementedError

    @classmethod
    def _obj_to_row(cls, data: T) -> dict[str, Any]:
        raise NotImplementedError

    @classmethod
    def _list_by_column(
        cls,
        column: str,
        value: str,
        conn: sqlite3.Connection | None = None,
        order_by: str | None = None,
    ) -> list[T]:
        query = f"SELECT {', '.join(cls._columns)} FROM {cls._table} WHERE {column} = ?"
        if order_by is not None:
            query = f"{query} ORDER BY {order_by}"
        if conn is None:
            with cls._connect() as local_conn:
                rows = local_conn.execute(query, (value,)).fetchall()
        else:
            rows = conn.execute(query, (value,)).fetchall()
        return [cls._row_to_obj(row) for row in rows]

    @classmethod
    def get_by_id(
        cls, id: uuid.UUID, conn: sqlite3.Connection | None = None
    ) -> T | None:
        query = f"SELECT {', '.join(cls._columns)} FROM {cls._table} WHERE id = ?"
        if conn is None:
            with cls._connect() as local_conn:
                row = local_conn.execute(query, (str(id),)).fetchone()
        else:
            row = conn.execute(query, (str(id),)).fetchone()
        if row is None:
            return None
        return cls._row_to_obj(row)

    @classmethod
    def list(cls, conn: sqlite3.Connection | None = None) -> list[T]:
        query = f"SELECT {', '.join(cls._columns)} FROM {cls._table}"
        if conn is None:
            with cls._connect() as local_conn:
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
        values = cls._obj_to_row(data)
        if "id" not in values:
            values["id"] = str(id)
        columns = ", ".join(values.keys())
        placeholders = ", ".join(["?"] * len(values))
        query = (
            f"INSERT OR REPLACE INTO {cls._table} ({columns}) VALUES ({placeholders})"
        )
        if conn is None:
            with cls._connect() as local_conn:
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
        cls.create(id, data, conn=conn)

    @classmethod
    def delete(cls, id: uuid.UUID, conn: sqlite3.Connection | None = None):
        query = f"DELETE FROM {cls._table} WHERE id = ?"
        if conn is None:
            with cls._connect() as local_conn:
                local_conn.execute(query, (str(id),))
                local_conn.commit()
        else:
            conn.execute(query, (str(id),))


@contextmanager
def transaction() -> Generator[sqlite3.Connection, None, None]:
    db_path = os.environ.get("INTERVIEW_DB_PATH", "interview.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    BaseModel._init_db(conn, db_path)
    try:
        conn.execute("BEGIN")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


class UserFilterMixin(Generic[T]):
    @classmethod
    def list_by_user(
        cls, user_id: uuid.UUID, conn: sqlite3.Connection | None = None
    ) -> list[T]:
        model = cast(_ColumnFilterable[T], cls)
        return model._list_by_column("user_id", str(user_id), conn)


class AreaFilterMixin(Generic[T]):
    @classmethod
    def list_by_area(
        cls, area_id: uuid.UUID, conn: sqlite3.Connection | None = None
    ) -> list[T]:
        model = cast(_ColumnFilterable[T], cls)
        return model._list_by_column("area_id", str(area_id), conn)


@dataclass
class User:
    id: uuid.UUID
    name: str
    mode: str


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


class UsersManager(BaseModel[User]):
    _table = "users"
    _columns = ("id", "name", "mode")

    @classmethod
    def _row_to_obj(cls, row: sqlite3.Row) -> User:
        return User(id=uuid.UUID(row["id"]), name=row["name"], mode=row["mode"])

    @classmethod
    def _obj_to_row(cls, data: User) -> dict[str, Any]:
        return {"id": str(data.id), "name": data.name, "mode": data.mode}


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
