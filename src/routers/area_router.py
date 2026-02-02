from langchain.tools import tool
from typing import Literal
import uuid

from langchain.tools import tool
from langchain_core.messages.tool import ToolCall

from src import db

MAX_LOOP_STEPS = 3


def _str_to_uuid(value: str | None) -> uuid.UUID | None:
    if value is None:
        return None
    try:
        return uuid.UUID(value)
    except ValueError:
        raise ValueError(f"Invalid UUID string format: {value}")


async def call_tool(tool_call: ToolCall):
    tool_name = tool_call["name"]
    tool_args = tool_call.get("args", {})

    tool_map = {t.name: t for t in AREA_TOOLS}
    tool_fn = tool_map.get(tool_name)

    if tool_fn is None:
        raise KeyError(f"Unknown tool: {tool_name}")

    return tool_fn.invoke(tool_args)


class LifeAreaMethods:
    @staticmethod
    def list(user_id: str) -> list[db.LifeAreaObject]:
        u_id = _str_to_uuid(user_id)
        return [obj for obj in db.LifeArea.list() if obj.user_id == u_id]

    @staticmethod
    def get(user_id: str, area_id: str) -> db.LifeAreaObject:
        u_id = _str_to_uuid(user_id)
        a_id = _str_to_uuid(area_id)

        if u_id is None or a_id is None:
            raise KeyError

        area = db.LifeArea.get_by_id(a_id)
        if area is None:
            raise KeyError(f"LifeArea {area_id} not found")

        if area.user_id != u_id:
            raise KeyError(f"LifeArea {area_id} does not belong to user {user_id}")

        return area

    @staticmethod
    def create(
        user_id: str, title: str, parent_id: str | None = None
    ) -> db.LifeAreaObject:
        u_id = _str_to_uuid(user_id)
        p_id = _str_to_uuid(parent_id)

        if u_id is None:
            raise KeyError

        area_id = uuid.uuid4()
        area = db.LifeAreaObject(id=area_id, title=title, parent_id=p_id, user_id=u_id)
        db.LifeArea.create(area_id, area)
        return area

    @staticmethod
    def delete(user_id: str, area_id: str) -> None:
        u_id = _str_to_uuid(user_id)
        a_id = _str_to_uuid(area_id)

        if u_id is None or a_id is None:
            raise KeyError

        area = db.LifeArea.get_by_id(a_id)
        if area is None:
            raise KeyError
        if area.user_id != u_id:
            raise KeyError

        db.LifeArea.delete(a_id)


class CriteriaMethods:
    @staticmethod
    def list(user_id: str, area_id: str) -> list[db.CriteriaObject]:
        area = LifeAreaMethods.get(user_id, area_id)

        return [obj for obj in db.Criteria.list() if obj.area_id == area.id]

    @staticmethod
    def delete(user_id: str, criteria_id: str) -> None:
        u_id = _str_to_uuid(user_id)
        c_id = _str_to_uuid(criteria_id)

        if u_id is None or c_id is None:
            raise KeyError

        criteria = db.Criteria.get_by_id(c_id)
        if criteria is None:
            raise KeyError
        area = LifeAreaMethods.get(user_id, str(criteria.area_id))

        if area.user_id != u_id:
            raise KeyError

        db.Criteria.delete(c_id)

    @staticmethod
    def create(user_id: str, area_id: str, title: str) -> db.CriteriaObject:
        area = LifeAreaMethods.get(user_id, area_id)

        criteria_id = uuid.uuid4()
        criteria = db.CriteriaObject(id=criteria_id, title=title, area_id=area.id)
        db.Criteria.create(criteria_id, criteria)
        return criteria


@tool
def list_life_areas(user_id: str) -> list[db.LifeAreaObject]:
    """List all life areas for a user."""
    return LifeAreaMethods.list(user_id)


@tool
def get_life_area(user_id: str, area_id: str) -> db.LifeAreaObject:
    """Fetch a single life area by id for a user."""
    return LifeAreaMethods.get(user_id, area_id)


@tool
def create_life_area(
    user_id: str, title: str, parent_id: str | None = None
) -> db.LifeAreaObject:
    """Create a new life area for a user."""
    return LifeAreaMethods.create(user_id, title, parent_id)


@tool
def delete_life_area(user_id: str, area_id: str) -> None:
    """Delete a life area by id for a user."""
    LifeAreaMethods.delete(user_id, area_id)


@tool
def list_criteria(user_id: str, area_id: str) -> list[db.CriteriaObject]:
    """List criteria belonging to a life area."""
    return CriteriaMethods.list(user_id, area_id)


@tool
def delete_criteria(user_id: str, criteria_id: str) -> None:
    """Delete a criteria item by id for a user."""
    CriteriaMethods.delete(user_id, criteria_id)


@tool
def create_criteria(user_id: str, area_id: str, title: str) -> db.CriteriaObject:
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


def route_area(state: dict) -> Literal["area_threshold", "area_tools", "area_end"]:
    if state["loop_step"] > MAX_LOOP_STEPS:
        return "area_threshold"
    if state["messages"][-1].tool_calls:
        return "area_tools"
    return "area_end"
