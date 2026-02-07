"""Knowledge extraction nodes for extract_data workflow."""

import json
import logging
from typing import Literal

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from src.infrastructure.db import repositories as db
from src.shared.ids import new_id
from src.shared.timestamp import get_timestamp

from .state import KnowledgeExtractionState

logger = logging.getLogger(__name__)

_KNOWLEDGE_EXTRACTION_PROMPT = (
    "You are a knowledge extraction agent.\n"
    "Your task is to extract discrete pieces of knowledge about the user "
    "from interview summaries.\n\n"
    "Extract two types of knowledge:\n"
    "1. SKILLS: Abilities, competencies, tools, technologies, languages, "
    "methodologies the user knows or is learning.\n"
    "   Examples: 'Python programming', 'project management', 'Spanish language'\n\n"
    "2. FACTS: Concrete information about the user's life.\n"
    "   Examples: 'Works at Google', 'Has 5 years experience', "
    "'Lives in San Francisco', 'Prefers remote work'\n\n"
    "Rules:\n"
    "- Be specific: 'Python backend development' not just 'programming'\n"
    "- Extract only what is clearly stated or strongly implied\n"
    "- Set confidence based on how explicitly the information was stated:\n"
    "  - 1.0: Directly stated ('I work at Google')\n"
    "  - 0.7-0.9: Strongly implied or mostly clear\n"
    "  - 0.5-0.7: Inferred but less certain\n"
    "- Do not invent or assume information not present in the summary\n"
)


class KnowledgeItem(BaseModel):
    """A single piece of extracted knowledge."""

    content: str = Field(description="The skill or fact description")
    kind: Literal["skill", "fact"] = Field(
        description="Type of knowledge: 'skill' for abilities/competencies, 'fact' for other information"
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence score based on how explicitly stated"
    )


class KnowledgeExtractionResult(BaseModel):
    """Result of knowledge extraction from a summary."""

    items: list[KnowledgeItem] = Field(
        default_factory=list, description="List of extracted knowledge items"
    )


def _resolve_summary_content(state: KnowledgeExtractionState) -> str:
    """Resolve summary content from state, computing from extracted_summary if needed."""
    from .nodes import _build_summary_content

    if state.summary_content:
        return state.summary_content
    if state.extracted_summary:
        content = _build_summary_content(state.extracted_summary)
        logger.info(
            "Computed summary_content from extracted_summary",
            extra={"area_id": str(state.area_id), "content_length": len(content)},
        )
        return content
    return ""


async def extract_knowledge(state: KnowledgeExtractionState, llm: ChatOpenAI) -> dict:
    """Extract skills and facts from the summary content using LLM.

    This node uses structured output to extract:
    - Skills: abilities, competencies, tools, technologies
    - Facts: employment, education, preferences, experiences, relationships
    """
    logger.info(
        "Starting knowledge extraction",
        extra={
            "area_id": str(state.area_id),
            "has_content": bool(state.summary_content),
        },
    )

    summary_content = _resolve_summary_content(state)
    if not summary_content:
        logger.info(
            "Skipping knowledge extraction - no summary content",
            extra={"area_id": str(state.area_id)},
        )
        return {"extracted_knowledge": []}

    user_prompt = {"area": state.area_title, "summary": summary_content}
    structured_llm = llm.with_structured_output(KnowledgeExtractionResult)

    try:
        result = await structured_llm.ainvoke(
            [
                {"role": "system", "content": _KNOWLEDGE_EXTRACTION_PROMPT},
                {"role": "user", "content": json.dumps(user_prompt)},
            ]
        )
        if not isinstance(result, KnowledgeExtractionResult):
            result = KnowledgeExtractionResult.model_validate(result)

        extracted = [item.model_dump() for item in result.items]
        logger.info(
            "Extracted knowledge items",
            extra={"area_id": str(state.area_id), "items_count": len(extracted)},
        )
        return {"extracted_knowledge": extracted}

    except Exception:
        logger.exception(
            "Failed to extract knowledge", extra={"area_id": str(state.area_id)}
        )
        return {"extracted_knowledge": []}


async def save_knowledge(state: KnowledgeExtractionState) -> dict:
    """Save extracted knowledge items to database.

    This node:
    1. For each extracted item, saves to user_knowledge table
    2. Links knowledge to user and area via user_knowledge_areas table

    Note: Duplicate detection is not implemented yet - each extraction
    creates new records. Future versions may implement fuzzy matching.
    """
    from src.infrastructure.db.connection import get_connection

    if not state.extracted_knowledge or not state.user_id:
        logger.info(
            "Skipping knowledge save - no knowledge or user_id",
            extra={
                "area_id": str(state.area_id),
                "has_user_id": state.user_id is not None,
                "knowledge_count": len(state.extracted_knowledge),
            },
        )
        return {}

    saved_count = 0
    with get_connection() as conn:
        for item in state.extracted_knowledge:
            knowledge_id = new_id()
            knowledge = db.UserKnowledge(
                id=knowledge_id,
                content=item["content"],
                kind=item["kind"],
                confidence=item["confidence"],
                created_ts=get_timestamp(),
            )
            db.UserKnowledgeManager.create(
                knowledge_id, knowledge, conn, auto_commit=False
            )

            link = db.UserKnowledgeArea(
                user_id=state.user_id,
                knowledge_id=knowledge_id,
                area_id=state.area_id,
            )
            db.UserKnowledgeAreasManager.create_link(link, conn, auto_commit=False)
            saved_count += 1
        conn.commit()

    logger.info(
        "Saved knowledge items",
        extra={
            "area_id": str(state.area_id),
            "user_id": str(state.user_id),
            "saved_count": saved_count,
        },
    )

    return {}
