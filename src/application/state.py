import enum
import uuid
from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, ConfigDict

from src.domain import ClientMessage, InputMode, User
from src.shared.interview_models import CriteriaAnalysis
from src.shared.message_buckets import MessageBuckets, merge_message_buckets


class Target(enum.Enum):
    """Interview workflow target."""

    interview = "interview"
    areas = "areas"

    @classmethod
    def from_user_mode(cls, mode: InputMode):
        """Convert user input mode to interview target.

        Args:
            mode: User input mode

        Returns:
            Target: Corresponding interview target

        Raises:
            NotImplementedError: If mode is not supported
        """
        match mode:
            case InputMode.interview:
                return cls.interview
            case InputMode.areas:
                return cls.areas
            case _:
                raise NotImplementedError()


class State(BaseModel):
    """Main LangGraph workflow state.

    Attributes:
        media_file: Path to temporary media file (e.g., uploaded video/audio)
        audio_file: Path to temporary extracted audio file (WAV format)
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    user: User
    message: ClientMessage
    media_file: str | None = None
    audio_file: str | None = None
    text: str
    target: Target
    messages: Annotated[list[BaseMessage], add_messages]
    messages_to_save: Annotated[MessageBuckets, merge_message_buckets]
    is_successful: bool | None = None
    area_id: uuid.UUID
    is_fully_covered: bool
    criteria_analysis: CriteriaAnalysis | None = None
