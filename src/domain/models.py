"""Domain models for the interview application."""

import enum
import io
import uuid
from dataclasses import dataclass

# User Models


class InputMode(enum.Enum):
    """User input mode for interview."""

    auto = "auto"
    interview = "interview"
    areas = "areas"


@dataclass
class User:
    """User profile during an active session."""

    id: uuid.UUID
    mode: InputMode
    current_life_area_id: uuid.UUID | None = None


class AccountGate(enum.Enum):
    """External account platforms."""

    telegram = "telegram"


@dataclass
class UserAccount:
    """User account connected to an external platform."""

    gate: AccountGate
    user: User
    external_id: str


# Message Models


class MessageType(enum.Enum):
    """Types of media messages."""

    audio = "audio"
    video = "video"


@dataclass(frozen=True)
class MediaMessage:
    """Media message (audio/video)."""

    type: MessageType
    content: io.BytesIO


@dataclass(frozen=True)
class ClientMessage:
    """Client message - can be text or media."""

    data: str | MediaMessage
