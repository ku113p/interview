"""State models for knowledge_extraction workflow."""

import uuid

from pydantic import BaseModel


class KnowledgeExtractionState(BaseModel):
    """State for the knowledge_extraction workflow."""

    # Core identifier - the summary to process
    summary_id: uuid.UUID

    # Loaded from DB via summary
    summary_text: str = ""
    summary_content: str = ""  # alias used by extract_knowledge
    area_id: uuid.UUID | None = None

    # Embedding vector from vectorize_summary
    summary_vector: list[float] | None = None

    # Extracted knowledge items: [{"content": str, "kind": str, "confidence": float}]
    extracted_knowledge: list[dict] = []
