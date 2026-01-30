from dataclasses import dataclass
import enum
from functools import cached_property
import io


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
