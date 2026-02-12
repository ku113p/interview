"""Domain model dataclasses for database entities."""

import uuid
from dataclasses import dataclass


@dataclass
class User:
    id: uuid.UUID
    name: str
    mode: str
    current_area_id: uuid.UUID | None = None


@dataclass(frozen=True)
class History:
    id: uuid.UUID
    message_data: dict
    user_id: uuid.UUID
    created_ts: float


@dataclass
class LifeArea:
    id: uuid.UUID
    title: str
    parent_id: uuid.UUID | None
    user_id: uuid.UUID
    extracted_at: float | None = None


@dataclass
class LifeAreaMessage:
    id: uuid.UUID
    message_text: str
    area_id: uuid.UUID
    created_ts: float
    leaf_ids: list[str] | None = None  # JSON array of leaf UUIDs this message answers


@dataclass
class AreaSummary:
    id: uuid.UUID
    area_id: uuid.UUID
    summary_text: str
    vector: list[float]
    created_ts: float


@dataclass
class UserKnowledge:
    id: uuid.UUID
    description: str
    kind: str  # 'skill' or 'fact'
    confidence: float
    created_ts: float


@dataclass
class UserKnowledgeArea:
    user_id: uuid.UUID
    knowledge_id: uuid.UUID
    area_id: uuid.UUID


@dataclass
class LeafCoverage:
    """Coverage status for a single leaf area in an interview."""

    leaf_id: uuid.UUID
    root_area_id: uuid.UUID
    status: str  # 'pending', 'active', 'covered', 'skipped'
    updated_at: float
    summary_text: str | None = None
    vector: list[float] | None = None


@dataclass
class ActiveInterviewContext:
    """Current interview state per user."""

    user_id: uuid.UUID
    root_area_id: uuid.UUID
    active_leaf_id: uuid.UUID
    created_at: float
    question_text: str | None = None
    message_ids: list[str] | None = None  # JSON array of message IDs


@dataclass
class LeafExtractionQueueItem:
    """An extraction task in the queue."""

    id: uuid.UUID
    leaf_id: uuid.UUID
    root_area_id: uuid.UUID
    message_ids: list[str]  # JSON array of message IDs
    created_at: float
    status: str = "pending"  # 'pending', 'processing', 'completed', 'failed'
    retry_count: int = 0
    processed_at: float | None = None
