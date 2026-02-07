"""Nodes for extract_data workflow."""

import json
import logging

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from src.infrastructure.db import repositories as db
from src.shared.ids import new_id
from src.shared.timestamp import get_timestamp

# Re-export knowledge nodes for backward compatibility
from .knowledge_nodes import (
    KnowledgeExtractionResult,
    KnowledgeItem,
    extract_knowledge,
    save_knowledge,
)
from .state import KnowledgeExtractionState

logger = logging.getLogger(__name__)

# Sentinel value used in LLM prompts for criteria without user responses
NO_RESPONSE_SENTINEL = "No response provided"

# Export all public names
__all__ = [
    "CriterionSummary",
    "ExtractionResult",
    "KnowledgeExtractionResult",
    "KnowledgeItem",
    "NO_RESPONSE_SENTINEL",
    "_build_summary_content",
    "extract_knowledge",
    "extract_summaries",
    "load_area_data",
    "save_knowledge",
    "save_summary",
]


class CriterionSummary(BaseModel):
    """Summary of user responses for a single criterion."""

    criterion: str
    summary: str


class ExtractionResult(BaseModel):
    """Structured extraction result from LLM."""

    summaries: list[CriterionSummary]


async def load_area_data(state: KnowledgeExtractionState) -> dict:
    """Load area data including title, criteria, and messages."""
    area_id = state.area_id

    area = db.LifeAreaManager.get_by_id(area_id)
    if area is None:
        logger.warning("Area not found for extraction", extra={"area_id": str(area_id)})
        return {"success": False}

    criteria = db.CriteriaManager.list_by_area(area_id)
    messages = db.LifeAreaMessagesManager.list_by_area(area_id)

    logger.info(
        "Loaded area data for extraction",
        extra={
            "area_id": str(area_id),
            "criteria_count": len(criteria),
            "message_count": len(messages),
        },
    )

    return {
        "area_title": area.title,
        "criteria_titles": [c.title for c in criteria],
        "messages": [m.data for m in messages],
    }


async def extract_summaries(state: KnowledgeExtractionState, llm: ChatOpenAI) -> dict:
    """Use LLM to extract and summarize user responses for each criterion.

    Note: The check for empty criteria/messages is handled by the router,
    so this function assumes valid data is present.
    """
    system_prompt = (
        "You are an interview data extraction agent.\n"
        "Your task is to summarize what the user said about each criterion.\n\n"
        "Rules:\n"
        "- For each criterion, extract a concise summary of the user's responses\n"
        "- Focus on facts and specific details the user shared\n"
        f"- If a criterion has no relevant responses, set summary to '{NO_RESPONSE_SENTINEL}'\n"
        "- Keep summaries brief but informative (1-3 sentences)\n"
    )

    user_prompt = {
        "area": state.area_title,
        "criteria": state.criteria_titles,
        "interview_messages": state.messages,
    }

    structured_llm = llm.with_structured_output(ExtractionResult)

    try:
        result = await structured_llm.ainvoke(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_prompt)},
            ]
        )

        if not isinstance(result, ExtractionResult):
            result = ExtractionResult.model_validate(result)

        extracted = {s.criterion: s.summary for s in result.summaries}

        logger.info(
            "Extracted summaries",
            extra={
                "area_id": str(state.area_id),
                "criteria_extracted": len(extracted),
            },
        )

        return {"extracted_summary": extracted, "success": True}

    except Exception:
        logger.exception(
            "Failed to extract summaries", extra={"area_id": str(state.area_id)}
        )
        return {"success": False}


def _build_summary_content(extracted_summary: dict[str, str]) -> str:
    """Combine extracted summaries into a single text for embedding."""
    parts = []
    for criterion, summary in extracted_summary.items():
        if summary and summary != NO_RESPONSE_SENTINEL:
            parts.append(f"{criterion}: {summary}")
    return "\n".join(parts)


async def save_summary(state: KnowledgeExtractionState) -> dict:
    """Save summary with embedding to area_summaries table.

    This node:
    1. Combines extracted summaries into a single content string
    2. Generates an embedding vector for the content
    3. Saves to area_summaries table

    Note: The success check is handled by the router before this node.
    """
    from src.infrastructure.embeddings import get_embedding_client

    summary_content = _build_summary_content(state.extracted_summary)

    if not summary_content:
        logger.info(
            "Skipping summary save - no meaningful content",
            extra={"area_id": str(state.area_id)},
        )
        return {"summary_content": ""}

    embed_client = get_embedding_client()
    try:
        embedding = await embed_client.aembed_query(summary_content)
    except Exception:
        logger.exception(
            "Failed to generate embedding for summary",
            extra={"area_id": str(state.area_id)},
        )
        return {"summary_content": ""}

    summary_id = new_id()
    area_summary = db.AreaSummary(
        id=summary_id,
        area_id=state.area_id,
        content=summary_content,
        vector=embedding,
        created_ts=get_timestamp(),
    )
    db.AreaSummariesManager.create(summary_id, area_summary)

    logger.info(
        "Saved area summary with embedding",
        extra={
            "area_id": str(state.area_id),
            "summary_id": str(summary_id),
            "content_length": len(summary_content),
        },
    )

    return {"summary_content": summary_content}
