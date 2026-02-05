import uuid

from uuid_extensions import uuid7


def new_id() -> uuid.UUID:
    """Generate a new UUID v7 (time-based, sortable).

    Returns:
        uuid.UUID: New UUID v7
    """
    return uuid7()
