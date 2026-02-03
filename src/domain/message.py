import enum
import io
from dataclasses import dataclass


class MessageType(enum.Enum):
    audio = "audio"
    video = "video"


@dataclass(frozen=True)
class MediaMessage:
    type: MessageType
    content: io.BytesIO


@dataclass(frozen=True)
class ClientMessage:
    data: str | MediaMessage
