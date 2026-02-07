"""State models for knowledge_extraction workflow."""

import uuid

from pydantic import BaseModel


class KnowledgeExtractionState(BaseModel):
    """State for the knowledge_extraction workflow."""

    # Core identifiers
    area_id: uuid.UUID
    user_id: uuid.UUID | None = None

    # Area data loaded from database
    area_title: str = ""
    criteria_titles: list[str] = []
    messages: list[str] = []

    # Extraction results
    extracted_summary: dict[str, str] = {}
    success: bool = False

    # Summary content for embedding (combined from extracted_summary)
    summary_content: str = ""

    # Extracted knowledge items: [{"content": str, "kind": str, "confidence": float}]
    extracted_knowledge: list[dict] = []
