"""Leaf interview subgraph state."""

import uuid
from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, ConfigDict

from src.domain.models import User
from src.shared.interview_models import LeafEvaluation
from src.shared.message_buckets import MessageBuckets, merge_message_buckets


class LeafInterviewState(BaseModel):
    """State for the leaf interview subgraph."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Input from parent
    user: User
    area_id: uuid.UUID
    messages: Annotated[list[BaseMessage], add_messages]
    area_already_extracted: bool = False

    # Working state (set during subgraph execution)
    active_leaf_id: uuid.UUID | None = None
    question_text: str | None = None
    all_leaves_done: bool = False
    leaf_evaluation: LeafEvaluation | None = None

    # Deferred DB write data (collected for atomic persist in save_history)
    turn_summary_text: str | None = None  # Summary of this turn (deferred write)
    set_covered_at: bool = False  # Signal to save_history to set covered_at

    # Output
    messages_to_save: Annotated[MessageBuckets, merge_message_buckets]
    is_successful: bool | None = None
    completed_leaf_id: uuid.UUID | None = None
    completed_leaf_path: str | None = None
    is_fully_covered: bool = False
