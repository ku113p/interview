import inspect
import logging
import sqlite3
import uuid
from functools import wraps
from typing import Callable

from langchain.tools import tool
from langchain_core.messages.tool import ToolCall

from src.infrastructure.db import repositories as db
from src.shared.ids import new_id

logger = logging.getLogger(__name__)


def _str_to_uuid(value: str | None) -> uuid.UUID | None:
    if value is None:
        return None
    return uuid.UUID(value)


def _validate_uuid(value: str | None, name: str) -> None:
    if value is None:
        return
    try:
        uuid.UUID(value)
    except ValueError as exc:
        logger.warning("Invalid UUID input", extra={"param": name})
        raise ValueError(f"Invalid UUID for {name}: {value}") from exc


def validate_uuid_args(*param_names: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        sig = inspect.signature(func)
        param_list = list(sig.parameters.keys())

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Validate keyword arguments
            for name in param_names:
                if name in kwargs:
                    _validate_uuid(kwargs[name], name)

            # Validate positional arguments
            for i, arg in enumerate(args):
                if i < len(param_list) and param_list[i] in param_names:
                    _validate_uuid(arg, param_list[i])

            return func(*args, **kwargs)

        return wrapper

    return decorator


async def call_tool(tool_call: ToolCall, conn: sqlite3.Connection | None = None):
    tool_name = tool_call["name"]
    tool_args = dict(tool_call.get("args", {}) or {})
    tool_args.pop("conn", None)

    tool_fn = TOOL_METHODS.get(tool_name)

    if tool_fn is None:
        raise KeyError(f"Unknown tool: {tool_name}")
    logger.info(
        "Calling tool",
        extra={"tool_name": tool_name, "arg_keys": list(tool_args.keys())},
    )
    return tool_fn(**tool_args, conn=conn)


class LifeAreaMethods:
    @staticmethod
    def list(user_id: str, conn: sqlite3.Connection | None = None) -> list[db.LifeArea]:
        u_id = _str_to_uuid(user_id)
        return [
            obj for obj in db.LifeAreaManager.list(conn=conn) if obj.user_id == u_id
        ]

    @staticmethod
    def get(
        user_id: str, area_id: str, conn: sqlite3.Connection | None = None
    ) -> db.LifeArea:
        u_id = _str_to_uuid(user_id)
        a_id = _str_to_uuid(area_id)

        if u_id is None or a_id is None:
            raise KeyError

        area = db.LifeAreaManager.get_by_id(a_id, conn=conn)
        if area is None:
            raise KeyError(f"LifeArea {area_id} not found")

        if area.user_id != u_id:
            raise KeyError(f"LifeArea {area_id} does not belong to user {user_id}")

        return area

    @staticmethod
    def create(
        user_id: str,
        title: str,
        parent_id: str | None = None,
        conn: sqlite3.Connection | None = None,
    ) -> db.LifeArea:
        u_id = _str_to_uuid(user_id)
        p_id = _str_to_uuid(parent_id)

        if u_id is None:
            raise KeyError

        area_id = new_id()
        area = db.LifeArea(id=area_id, title=title, parent_id=p_id, user_id=u_id)
        db.LifeAreaManager.create(area_id, area, conn=conn)
        return area

    @staticmethod
    def delete(
        user_id: str, area_id: str, conn: sqlite3.Connection | None = None
    ) -> None:
        u_id = _str_to_uuid(user_id)
        a_id = _str_to_uuid(area_id)

        if u_id is None or a_id is None:
            raise KeyError

        area = db.LifeAreaManager.get_by_id(a_id, conn=conn)
        if area is None:
            raise KeyError
        if area.user_id != u_id:
            raise KeyError

        db.LifeAreaManager.delete(a_id, conn=conn)


class CriteriaMethods:
    @staticmethod
    def list(
        user_id: str, area_id: str, conn: sqlite3.Connection | None = None
    ) -> list[db.Criteria]:
        area = LifeAreaMethods.get(user_id, area_id, conn=conn)

        return [
            obj for obj in db.CriteriaManager.list(conn=conn) if obj.area_id == area.id
        ]

    @staticmethod
    def delete(
        user_id: str, criteria_id: str, conn: sqlite3.Connection | None = None
    ) -> None:
        u_id = _str_to_uuid(user_id)
        c_id = _str_to_uuid(criteria_id)
        if u_id is None or c_id is None:
            raise KeyError
        criteria = db.CriteriaManager.get_by_id(c_id, conn=conn)
        if criteria is None:
            raise KeyError
        area = LifeAreaMethods.get(user_id, str(criteria.area_id), conn=conn)
        if area.user_id != u_id:
            raise KeyError
        db.CriteriaManager.delete(c_id, conn=conn)

    @staticmethod
    def create(
        user_id: str,
        area_id: str,
        title: str,
        conn: sqlite3.Connection | None = None,
    ) -> db.Criteria:
        area = LifeAreaMethods.get(user_id, area_id, conn=conn)

        criteria_id = new_id()
        criteria = db.Criteria(id=criteria_id, title=title, area_id=area.id)
        db.CriteriaManager.create(criteria_id, criteria, conn=conn)
        return criteria


@tool
@validate_uuid_args("user_id")
def list_life_areas(user_id: str) -> list[db.LifeArea]:
    """List all life areas for a user."""
    return LifeAreaMethods.list(user_id)


@tool
@validate_uuid_args("user_id", "area_id")
def get_life_area(user_id: str, area_id: str) -> db.LifeArea:
    """Fetch a single life area by id for a user."""
    return LifeAreaMethods.get(user_id, area_id)


@tool
@validate_uuid_args("user_id", "parent_id")
def create_life_area(
    user_id: str, title: str, parent_id: str | None = None
) -> db.LifeArea:
    """Create a new life area for a user."""
    return LifeAreaMethods.create(user_id, title, parent_id)


@tool
@validate_uuid_args("user_id", "area_id")
def delete_life_area(user_id: str, area_id: str) -> None:
    """Delete a life area by id for a user."""
    LifeAreaMethods.delete(user_id, area_id)


@tool
@validate_uuid_args("user_id", "area_id")
def list_criteria(user_id: str, area_id: str) -> list[db.Criteria]:
    """List criteria belonging to a life area."""
    return CriteriaMethods.list(user_id, area_id)


@tool
@validate_uuid_args("user_id", "criteria_id")
def delete_criteria(user_id: str, criteria_id: str) -> None:
    """Delete a criteria item by id for a user."""
    CriteriaMethods.delete(user_id, criteria_id)


@tool
@validate_uuid_args("user_id", "area_id")
def create_criteria(user_id: str, area_id: str, title: str) -> db.Criteria:
    """Create a criteria item under a life area."""
    return CriteriaMethods.create(user_id, area_id, title)


AREA_TOOLS = [
    create_life_area,
    delete_life_area,
    get_life_area,
    list_life_areas,
    create_criteria,
    delete_criteria,
    list_criteria,
]

TOOL_METHODS = {
    "list_life_areas": LifeAreaMethods.list,
    "get_life_area": LifeAreaMethods.get,
    "create_life_area": LifeAreaMethods.create,
    "delete_life_area": LifeAreaMethods.delete,
    "list_criteria": CriteriaMethods.list,
    "delete_criteria": CriteriaMethods.delete,
    "create_criteria": CriteriaMethods.create,
}
