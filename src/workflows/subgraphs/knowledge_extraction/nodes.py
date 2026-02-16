"""Nodes for extract_data workflow."""

import json
import logging
import uuid

import aiosqlite
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from src.infrastructure.db import managers as db
from src.shared.ids import new_id
from src.shared.timestamp import get_timestamp
from src.shared.tree_utils import build_sub_area_info, build_tree_text

# Re-export knowledge nodes for backward compatibility
from .knowledge_nodes import (
    KnowledgeExtractionResult,
    KnowledgeItem,
    extract_knowledge,
)
from .state import KnowledgeExtractionState

logger = logging.getLogger(__name__)

# Sentinel value used in LLM prompts for sub-areas without user responses
NO_RESPONSE_SENTINEL = "No response provided"

# Export all public names
__all__ = [
    "SubAreaSummary",
    "ExtractionResult",
    "KnowledgeExtractionResult",
    "KnowledgeItem",
    "NO_RESPONSE_SENTINEL",
    "_build_summary_content",
    "extract_knowledge",
    "extract_summaries",
    "load_area_data",
    "persist_extraction",
    "prepare_summary",
]


class SubAreaSummary(BaseModel):
    """Summary of user responses for a single sub-area."""

    sub_area: str
    summary: str


class ExtractionResult(BaseModel):
    """Structured extraction result from LLM."""

    summaries: list[SubAreaSummary]


def _collect_leaf_summaries(
    leaf_coverage_list: list, sub_area_info: list
) -> dict[str, str]:
    """Collect summaries from covered leaves, mapping to their paths."""
    if not leaf_coverage_list:
        return {}

    leaf_id_to_path = {str(info.area.id): info.path for info in sub_area_info}
    summaries: dict[str, str] = {}

    for lc in leaf_coverage_list:
        if lc.status == "covered" and lc.summary_text:
            path = leaf_id_to_path.get(str(lc.leaf_id))
            if path:
                summaries[path] = lc.summary_text
    return summaries


async def _load_leaf_area_data(area: db.LifeArea, area_id: uuid.UUID) -> dict:
    """Load data for leaf area (no descendants) from leaf_coverage summary."""
    leaf_coverage = await db.LeafCoverageManager.get_by_id(area_id)
    if not leaf_coverage:
        logger.info("No coverage record for leaf area", extra={"area_id": str(area_id)})
        return {"is_successful": False}
    if not leaf_coverage.summary_text:
        logger.info(
            "Coverage record has no summary text", extra={"area_id": str(area_id)}
        )
        return {"is_successful": False}

    logger.info(
        "Loaded leaf area summary from coverage",
        extra={"area_id": str(area_id)},
    )
    return {
        "area_title": area.title,
        "sub_areas_tree": area.title,
        "sub_area_paths": [area.title],
        "messages": [],
        "extracted_summary": {area.title: leaf_coverage.summary_text},
        "use_leaf_summaries": True,
        "is_leaf": True,
        "user_id": area.user_id,
    }


async def _load_root_area_data(
    area: db.LifeArea, area_id: uuid.UUID, sub_areas: list[db.LifeArea]
) -> dict:
    """Load data for root area (has descendants) using leaf summaries."""
    tree_text = build_tree_text(sub_areas, area_id)
    sub_area_info = build_sub_area_info(sub_areas, area_id)
    sub_area_paths = [info.path for info in sub_area_info]

    leaf_coverage_list = await db.LeafCoverageManager.list_by_root_area(area_id)
    leaf_summaries = _collect_leaf_summaries(leaf_coverage_list, sub_area_info)

    if leaf_summaries:
        logger.info("Using leaf summaries", extra={"count": len(leaf_summaries)})
        return {
            "area_title": area.title,
            "sub_areas_tree": tree_text,
            "sub_area_paths": sub_area_paths,
            "messages": [],
            "extracted_summary": leaf_summaries,
            "use_leaf_summaries": True,
            "user_id": area.user_id,
        }

    logger.info(
        "No leaf summaries available for extraction",
        extra={"area_id": str(area_id), "sub_area_count": len(sub_area_paths)},
    )
    return {
        "area_title": area.title,
        "sub_areas_tree": tree_text,
        "sub_area_paths": sub_area_paths,
        "messages": [],
        "use_leaf_summaries": False,
        "is_successful": False,
    }


async def load_area_data(state: KnowledgeExtractionState) -> dict:
    """Load area data including title, sub-areas, and summaries.

    Handles two cases:
    1. Leaf area (no descendants): Read summary from leaf_coverage.summary_text
    2. Root area (has descendants): Use pre-extracted leaf summaries from leaf_coverage
    """
    area_id = state.area_id
    area = await db.LifeAreasManager.get_by_id(area_id)
    if area is None:
        logger.warning("Area not found", extra={"area_id": str(area_id)})
        return {"is_successful": False}

    sub_areas = await db.LifeAreasManager.get_descendants(area_id)
    if not sub_areas:
        return await _load_leaf_area_data(area, area_id)
    return await _load_root_area_data(area, area_id, sub_areas)


async def extract_summaries(state: KnowledgeExtractionState, llm: ChatOpenAI) -> dict:
    """Use LLM to extract and summarize user responses for each sub-area.

    If leaf summaries were already loaded (use_leaf_summaries=True), this node
    is skipped and the pre-extracted summaries are used directly.

    Note: The check for empty sub-areas/messages is handled by the router,
    so this function assumes valid data is present.
    """
    # Skip if we already have leaf summaries
    if state.use_leaf_summaries and state.extracted_summary:
        logger.info(
            "Skipping LLM extraction - using pre-extracted leaf summaries",
            extra={
                "area_id": str(state.area_id),
                "summary_count": len(state.extracted_summary),
            },
        )
        return {"is_successful": True}

    system_prompt = (
        "You are an interview data extraction agent.\n"
        "Your task is to summarize what the user said about each sub-area.\n\n"
        "The sub-areas are shown as a tree and as paths (like 'Work > Projects').\n"
        "Use the exact paths when outputting summaries.\n\n"
        "Rules:\n"
        "- For each sub-area path, extract a concise summary of the user's responses\n"
        "- Focus on facts and specific details the user shared\n"
        f"- If a sub-area has no relevant responses, set summary to '{NO_RESPONSE_SENTINEL}'\n"
        "- Keep summaries brief but informative (1-3 sentences)\n"
    )

    user_prompt = {
        "area": state.area_title,
        "sub_areas_tree": state.sub_areas_tree,
        "sub_area_paths": state.sub_area_paths,
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

        extracted = {s.sub_area: s.summary for s in result.summaries}

        logger.info(
            "Extracted summaries via LLM",
            extra={
                "area_id": str(state.area_id),
                "sub_areas_extracted": len(extracted),
            },
        )

        return {"extracted_summary": extracted, "is_successful": True}

    except Exception:
        logger.exception(
            "Failed to extract summaries", extra={"area_id": str(state.area_id)}
        )
        return {"is_successful": False}


def _build_summary_content(extracted_summary: dict[str, str]) -> str:
    """Combine extracted summaries into a single text for embedding."""
    parts = []
    for sub_area, summary in extracted_summary.items():
        if summary and summary != NO_RESPONSE_SENTINEL:
            parts.append(f"{sub_area}: {summary}")
    return "\n".join(parts)


async def prepare_summary(state: KnowledgeExtractionState) -> dict:
    """Generate embedding vector for the combined summary content.

    This node:
    1. Combines extracted summaries into a single content string
    2. Generates an embedding vector for the content
    3. Returns vector in state for atomic persistence in persist_extraction

    Note: The success check is handled by the router before this node.
    """
    from src.infrastructure.embeddings import get_embedding_client

    summary_content = _build_summary_content(state.extracted_summary)

    if not summary_content:
        logger.info(
            "Skipping summary - no meaningful content",
            extra={"area_id": str(state.area_id)},
        )
        return {"summary_content": ""}

    if not state.is_leaf:
        logger.info(
            "Skipping embedding for root area",
            extra={"area_id": str(state.area_id)},
        )
        return {"summary_content": summary_content}

    embed_client = get_embedding_client()
    try:
        vector = await embed_client.aembed_query(summary_content)
    except Exception:
        logger.exception(
            "Failed to generate embedding for summary",
            extra={"area_id": str(state.area_id)},
        )
        return {"summary_content": summary_content}

    logger.info(
        "Prepared summary embedding",
        extra={
            "area_id": str(state.area_id),
            "content_length": len(summary_content),
        },
    )

    return {"summary_content": summary_content, "summary_vector": vector}


async def _save_knowledge_items(
    state: KnowledgeExtractionState, now: float, conn: aiosqlite.Connection
) -> int:
    """Save extracted knowledge items and area links within a transaction."""
    saved_count = 0
    for item in state.extracted_knowledge:
        knowledge_id = new_id()
        knowledge = db.UserKnowledge(
            id=knowledge_id,
            description=item["content"],
            kind=item["kind"],
            confidence=item["confidence"],
            created_ts=now,
        )
        await db.UserKnowledgeManager.create(
            knowledge_id, knowledge, conn, auto_commit=False
        )
        link = db.UserKnowledgeArea(
            knowledge_id=knowledge_id,
            area_id=state.area_id,
        )
        await db.UserKnowledgeAreasManager.create_link(link, conn, auto_commit=False)
        saved_count += 1
    return saved_count


async def persist_extraction(state: KnowledgeExtractionState) -> dict:
    """Persist all extraction results atomically.

    Writes vector, knowledge items, and mark_extracted in one transaction.
    """
    from src.infrastructure.db.connection import transaction

    now = get_timestamp()
    async with transaction() as conn:
        # 1. Save leaf vector (for leaf areas)
        if state.summary_vector:
            await db.LeafCoverageManager.update_vector(
                state.area_id, state.summary_vector, now, conn=conn
            )

        # 2. Save knowledge items + area links
        saved_count = 0
        if state.extracted_knowledge and state.user_id:
            saved_count = await _save_knowledge_items(state, now, conn)

        # 3. Mark area extracted
        await db.LifeAreasManager.mark_extracted(
            state.area_id, conn=conn, timestamp=now
        )

    logger.info(
        "Persisted extraction atomically",
        extra={
            "area_id": str(state.area_id),
            "has_vector": bool(state.summary_vector),
            "knowledge_count": saved_count,
        },
    )
    return {}
