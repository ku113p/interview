import uuid

from langchain.tools import tool

from src import db

def _str_to_uuid(value: str | None) -> uuid.UUID | None:
    """Helper to safely parse string to UUID."""
    if value is None:
        return None
    try:
        return uuid.UUID(value)
    except ValueError:
        raise ValueError(f"Invalid UUID string format: {value}")

class LifeAreaMethods:
    @tool
    @staticmethod
    def list(user_id: str) -> list[db.LifeAreaObject]:
        """List all life areas for a specific user."""
        u_id = _str_to_uuid(user_id)
        return [obj for obj in db.LifeArea.list() if obj.user_id == u_id]

    @tool
    @staticmethod
    def get(user_id: str, area_id: str) -> db.LifeAreaObject:
        """Get a specific life area by ID."""
        u_id = _str_to_uuid(user_id)
        a_id = _str_to_uuid(area_id)
        
        area = db.LifeArea.get_by_id(a_id)
        if area.user_id != u_id:
            raise KeyError(f"LifeArea {area_id} does not belong to user {user_id}")
        
        return area
    
    @tool
    @staticmethod
    def create(user_id: str, title: str, parent_id: str | None = None) -> db.LifeAreaObject:
        """Create a new life area."""
        u_id = _str_to_uuid(user_id)
        p_id = _str_to_uuid(parent_id)
        
        area_id = uuid.uuid7()
        area = db.LifeAreaObject(id=area_id, title=title, parent_id=p_id, user_id=u_id)
        db.LifeArea.create(area_id, area)
        return area
    
    @tool
    @staticmethod
    def delete(user_id: str, area_id: str) -> None:
        """Delete a life area."""
        u_id = _str_to_uuid(user_id)
        a_id = _str_to_uuid(area_id)
        
        area = db.LifeArea.get_by_id(a_id)
        if area.user_id != u_id:
            raise KeyError
        
        db.LifeArea.delete(a_id)


class CriteriaMethods:
    @tool
    @staticmethod
    def list(user_id: str, area_id: str) -> list[db.CriteriaObject]:
        """List criteria associated with a specific life area."""
        # We can pass the strings directly because LifeAreaMethods.get now accepts strings
        area = LifeAreaMethods.get(user_id, area_id)

        return [obj for obj in db.Criteria.list() if obj.area_id == area.id]
    
    @tool
    @staticmethod
    def delete(user_id: str, criteria_id: str) -> None:
        """Delete a criteria."""
        u_id = _str_to_uuid(user_id)
        c_id = _str_to_uuid(criteria_id)
        
        criteria = db.Criteria.get_by_id(c_id)
        
        # We convert the area_id from the object back to string to use the helper tool, 
        # or we could implement raw logic here. Using the tool keeps it consistent.
        area = LifeAreaMethods.get(user_id, str(criteria.area_id))
        
        if area.user_id != u_id:
            raise KeyError
        
        db.Criteria.delete(c_id)
    
    @tool
    @staticmethod
    def create(user_id: str, area_id: str, title: str) -> db.CriteriaObject:
        """Create a new criteria for a life area."""
        # Validation happens inside LifeAreaMethods.get
        area = LifeAreaMethods.get(user_id, area_id)

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