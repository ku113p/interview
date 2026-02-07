"""Nodes for extract_data workflow."""

import json
import logging

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from src.infrastructure.db import repositories as db
from src.shared.ids import new_id
from src.shared.timestamp import get_timestamp

from .state import ExtractDataState

logger = logging.getLogger(__name__)


class CriterionSummary(BaseModel):
    """Summary of user responses for a single criterion."""

    criterion: str
    summary: str


class ExtractionResult(BaseModel):
    """Structured extraction result from LLM."""

    summaries: list[CriterionSummary]


async def load_area_data(state: ExtractDataState) -> dict:
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


async def extract_summaries(state: ExtractDataState, llm: ChatOpenAI) -> dict:
    """Use LLM to extract and summarize user responses for each criterion."""
    if not state.criteria_titles or not state.messages:
        logger.info(
            "Skipping extraction - no criteria or messages",
            extra={"area_id": str(state.area_id)},
        )
        return {"success": False}

    system_prompt = (
        "You are an interview data extraction agent.\n"
        "Your task is to summarize what the user said about each criterion.\n\n"
        "Rules:\n"
        "- For each criterion, extract a concise summary of the user's responses\n"
        "- Focus on facts and specific details the user shared\n"
        "- If a criterion has no relevant responses, set summary to 'No response provided'\n"
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


async def save_extracted_data(state: ExtractDataState) -> dict:
    """Save extracted data to the database."""
    if not state.success or not state.extracted_summary:
        logger.info(
            "Skipping save - extraction not successful",
            extra={"area_id": str(state.area_id)},
        )
        return {}

    data_id = new_id()
    extracted = db.ExtractedData(
        id=data_id,
        area_id=state.area_id,
        data=json.dumps(state.extracted_summary),
        created_ts=get_timestamp(),
    )
    db.ExtractedDataManager.create(data_id, extracted)

    logger.info(
        "Saved extracted data",
        extra={
            "area_id": str(state.area_id),
            "data_id": str(data_id),
        },
    )

    return {}
