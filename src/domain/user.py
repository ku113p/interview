import enum
import uuid
from dataclasses import dataclass


class InputMode(enum.Enum):
    auto = "auto"
    interview = "interview"
    areas = "areas"


@dataclass
class User:
    id: uuid.UUID
    mode: InputMode
    current_life_area_id: uuid.UUID | None = None


class AccountGate(enum.Enum):
    telegram = "telegram"


@dataclass
class UserAccount:
    gate: AccountGate
    user: User
    external_id: str
