"""Core repository managers: Users, History, LifeArea, Criteria."""

import json
import sqlite3
import uuid
from typing import Any

from .base import ORMBase
from .models import Criteria, History, LifeArea, User


class UsersManager(ORMBase[User]):
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


class HistoriesManager(ORMBase[History]):
    _table = "histories"
    _columns = ("id", "data", "user_id", "created_ts")
    _user_column = "user_id"

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


class LifeAreasManager(ORMBase[LifeArea]):
    _table = "life_areas"
    _columns = ("id", "title", "parent_id", "user_id")
    _user_column = "user_id"

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


class CriteriaManager(ORMBase[Criteria]):
    _table = "criteria"
    _columns = ("id", "title", "area_id")
    _area_column = "area_id"

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
