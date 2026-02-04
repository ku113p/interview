import uuid

from uuid_extensions import uuid7


def new_id() -> uuid.UUID:
    return uuid7()
