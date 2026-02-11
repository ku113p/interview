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
