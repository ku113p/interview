"""Nodes for knowledge_extraction workflow."""

import logging

import aiosqlite

from src.infrastructure.db import managers as db
from src.shared.ids import new_id
from src.shared.timestamp import get_timestamp

# Re-export knowledge nodes
from .knowledge_nodes import (
    KnowledgeExtractionResult,
    KnowledgeItem,
    extract_knowledge,
)
from .state import KnowledgeExtractionState

logger = logging.getLogger(__name__)

__all__ = [
    "KnowledgeExtractionResult",
    "KnowledgeItem",
    "extract_knowledge",
    "load_summary",
    "vectorize_summary",
    "persist_extraction",
]


async def load_summary(state: KnowledgeExtractionState) -> dict:
    """Load summary text and area_id from the database."""
    summary = await db.SummariesManager.get_by_id(state.summary_id)
    if not summary:
        logger.warning("Summary not found", extra={"summary_id": str(state.summary_id)})
        return {}
    return {
        "summary_text": summary.summary_text,
        "summary_content": summary.summary_text,
        "area_id": summary.area_id,
    }


async def vectorize_summary(state: KnowledgeExtractionState) -> dict:
    """Generate embedding vector for the summary text."""
    from src.infrastructure.embeddings import get_embedding_client

    try:
        vector = await get_embedding_client().aembed_query(state.summary_text)
        return {"summary_vector": vector}
    except Exception:
        logger.exception(
            "Embedding failed", extra={"summary_id": str(state.summary_id)}
        )
        return {}


async def _save_knowledge_items(
    state: KnowledgeExtractionState, now: float, conn: aiosqlite.Connection
) -> int:
    """Save extracted knowledge items within a transaction."""
    saved_count = 0
    for item in state.extracted_knowledge:
        knowledge_id = new_id()
        knowledge = db.UserKnowledge(
            id=knowledge_id,
            description=item["content"],
            kind=item["kind"],
            confidence=item["confidence"],
            created_ts=now,
            summary_id=state.summary_id,
        )
        await db.UserKnowledgeManager.create(
            knowledge_id, knowledge, conn, auto_commit=False
        )
        saved_count += 1
    return saved_count


async def persist_extraction(state: KnowledgeExtractionState) -> dict:
    """Persist extraction results: update summary vector and save knowledge items."""
    from src.infrastructure.db.connection import transaction

    now = get_timestamp()
    async with transaction() as conn:
        if state.summary_vector is not None:
            await db.SummariesManager.update_vector(
                state.summary_id, state.summary_vector, conn=conn
            )
        saved_count = 0
        if state.extracted_knowledge and state.area_id:
            saved_count = await _save_knowledge_items(state, now, conn)

    logger.info(
        "Persisted extraction",
        extra={
            "summary_id": str(state.summary_id),
            "knowledge_count": saved_count,
        },
    )
    return {}
