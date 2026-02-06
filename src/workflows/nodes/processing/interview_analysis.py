import asyncio
import json
import logging
import uuid
from typing import Annotated

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from pydantic import BaseModel, ConfigDict

from src.infrastructure.db import repositories as db
from src.shared.ids import new_id
from src.shared.interview_models import CriteriaAnalysis
from src.shared.message_buckets import MessageBuckets, merge_message_buckets
from src.shared.timestamp import get_timestamp
from src.shared.utils.content import normalize_content

logger = logging.getLogger(__name__)


class State(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    area_id: uuid.UUID
    extract_data_tasks: asyncio.Queue[uuid.UUID]
    messages: Annotated[list[BaseMessage], add_messages]
    messages_to_save: Annotated[MessageBuckets, merge_message_buckets]
    success: bool | None = None
    was_covered: bool
    criteria_analysis: CriteriaAnalysis | None = None


async def interview_analysis(state: State, llm: ChatOpenAI):
    """Analyze criteria coverage without generating response."""
    area_id = state.area_id
    message_content = normalize_content(state.messages[-1].content)

    # Save user message to area messages
    last_area_msg = db.LifeAreaMessage(
        id=new_id(),
        data=message_content,
        area_id=area_id,
        created_ts=get_timestamp(),
    )
    db.LifeAreaMessagesManager.create(last_area_msg.id, last_area_msg)

    # Get area data
    area_msgs: list[str] = [
        msg.data for msg in db.LifeAreaMessagesManager.list_by_area(area_id)
    ]
    area_criteria: list[str] = [
        c.title for c in db.CriteriaManager.list_by_area(area_id)
    ]

    # Analyze coverage (structured output)
    analysis = await _analyze_coverage(area_msgs, area_criteria, llm)

    if analysis.all_covered:
        await state.extract_data_tasks.put(area_id)

    logger.info(
        "Interview criteria analyzed",
        extra={
            "area_id": str(area_id),
            "message_count": len(area_msgs),
            "criteria_count": len(area_criteria),
            "all_covered": analysis.all_covered,
            "next_uncovered": analysis.next_uncovered,
        },
    )

    return {
        "criteria_analysis": analysis,
        "was_covered": analysis.all_covered,
    }


async def _analyze_coverage(
    interview_messages: list[str],
    area_criteria: list[str],
    llm: ChatOpenAI,
) -> CriteriaAnalysis:
    """Analyze which criteria are covered by the interview messages."""
    system_prompt = (
        "You are an interview analysis agent.\n"
        "Your task is to analyze the interview messages and determine:\n"
        "1. For EACH criterion, whether it is clearly covered by the interview\n"
        "2. Which criterion should be asked about next (if any remain uncovered)\n\n"
        "Rules:\n"
        "- Be strict: unclear or partial answers = NOT covered\n"
        "- If NO criteria exist, set all_covered=false and next_uncovered=null\n"
        "- Pick the most logical next criterion to ask about\n"
    )

    user_prompt = {
        "interview_messages": interview_messages,
        "criteria": area_criteria,
    }

    structured_llm = llm.with_structured_output(CriteriaAnalysis)

    result = await structured_llm.ainvoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_prompt)},
        ]
    )

    if not isinstance(result, CriteriaAnalysis):
        result = CriteriaAnalysis.model_validate(result)

    return result
