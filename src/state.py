import asyncio
import enum
import uuid
from typing import Annotated, BinaryIO

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, ConfigDict

from src.domain import message, user


class Target(enum.Enum):
    interview = "interview"
    areas = "areas"

    @classmethod
    def from_user_mode(cls, mode: user.InputMode):
        match mode:
            case user.InputMode.interview:
                return cls.interview
            case user.InputMode.areas:
                return cls.areas
            case _:
                raise NotImplementedError()


class State(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    user: user.User
    message: message.ClientMessage
    media_file: BinaryIO
    audio_file: BinaryIO
    text: str
    target: Target
    messages: Annotated[list[BaseMessage], add_messages]
    messages_to_save: Annotated[list[BaseMessage], add_messages]
    success: bool | None = None
    area_id: uuid.UUID
    extract_data_tasks: asyncio.Queue[uuid.UUID]
    was_covered: bool
