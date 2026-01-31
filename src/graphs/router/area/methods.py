import uuid

from langchain.tools import tool

from src import db


def parse_uuid(value: str) -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except ValueError:
        raise ValueError(f"Invalid UUID string format: {value}")


class LifeAreaMethods:
    @tool
    @staticmethod
    def list(user_id: str) -> list[db.LifeAreaObject]:
        u_id = parse_uuid(user_id)
        return [obj for obj in db.LifeArea.list() if obj.user_id == u_id]

    @tool
    @staticmethod
    def get(user_id: str, area_id: str) -> db.LifeAreaObject:
        u_id = parse_uuid(user_id)
        a_id = parse_uuid(area_id)
        area = db.LifeArea.get_by_id(a_id)
        if area is None:
            raise KeyError(f"LifeArea {area_id} not found")
        if area.user_id != u_id:
            raise KeyError(f"LifeArea {area_id} does not belong to user {user_id}")
        return area

    @tool
    @staticmethod
    def create(
        user_id: str, title: str, parent_id: str | None = None
    ) -> db.LifeAreaObject:
        u_id = parse_uuid(user_id)
        p_id = parse_uuid(parent_id) if parent_id is not None else None
        area_id = uuid.uuid7()
        area = db.LifeAreaObject(
            id=area_id,
            title=title,
            parent_id=p_id,
            user_id=u_id,
        )
        db.LifeArea.create(area_id, area)
        return area

    @tool
    @staticmethod
    def delete(user_id: str, area_id: str) -> None:
        u_id = parse_uuid(user_id)
        a_id = parse_uuid(area_id)
        area = db.LifeArea.get_by_id(a_id)
        if area is None:
            raise KeyError(f"LifeArea {area_id} not found")
        if area.user_id != u_id:
            raise KeyError
        db.LifeArea.delete(a_id)


class CriteriaMethods:
    @tool
    @staticmethod
    def list(user_id: str, area_id: str) -> list[db.CriteriaObject]:
        area = LifeAreaMethods.get.invoke({"user_id": user_id, "area_id": area_id})
        return [obj for obj in db.Criteria.list() if obj.area_id == area.id]

    @tool
    @staticmethod
    def delete(user_id: str, criteria_id: str) -> None:
        u_id = parse_uuid(user_id)
        c_id = parse_uuid(criteria_id)
        criteria = db.Criteria.get_by_id(c_id)
        if criteria is None:
            raise KeyError(f"Criteria {criteria_id} not found")
        area = LifeAreaMethods.get.invoke(
            {"user_id": user_id, "area_id": str(criteria.area_id)}
        )
        if area.user_id != u_id:
            raise KeyError
        db.Criteria.delete(c_id)

    @tool
    @staticmethod
    def create(user_id: str, area_id: str, title: str) -> db.CriteriaObject:
        area = LifeAreaMethods.get.invoke({"user_id": user_id, "area_id": area_id})
        criteria_id = uuid.uuid7()
        criteria = db.CriteriaObject(id=criteria_id, title=title, area_id=area.id)
        db.Criteria.create(criteria_id, criteria)
        return criteria


AREA_TOOLS = [
    LifeAreaMethods.create,
    LifeAreaMethods.delete,
    LifeAreaMethods.get,
    LifeAreaMethods.list,
    CriteriaMethods.create,
    CriteriaMethods.delete,
    CriteriaMethods.list,
]
