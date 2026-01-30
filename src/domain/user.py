from dataclasses import dataclass
import enum
import uuid


class InputMode(enum.Enum):
    auto = 'auto'
    interview = 'interview'
    areas = 'areas'


@dataclass
class User:
    id: uuid.UUID
    mode: InputMode


class AccountGate(enum.Enum):
    telegram = 'telegram'


@dataclass
class UserAccount:
    gate: AccountGate
    user: User
    external_id: str
