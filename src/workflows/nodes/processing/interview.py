import asyncio
import json
import logging
import uuid
from typing import Annotated

from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from src.infrastructure.db import repositories as db
from src.shared.ids import new_id
from src.shared.message_buckets import MessageBuckets, merge_message_buckets
from src.shared.timestamp import get_timestamp
from src.shared.utils.content import normalize_content

logger = logging.getLogger(__name__)


class State(BaseModel):
    area_id: uuid.UUID
    extract_data_tasks: asyncio.Queue[uuid.UUID]
    messages: Annotated[list[BaseMessage], add_messages]
    messages_to_save: Annotated[MessageBuckets, merge_message_buckets]
    success: bool | None = None
    was_covered: bool

    class Config:
        arbitrary_types_allowed = True


class CriterionCoverage(BaseModel):
    title: str
    covered: bool


class CriteriaCoverageResult(BaseModel):
    criteria: list[CriterionCoverage]
    all_covered: bool
    final_answer: str


async def interview(state: State, llm: ChatOpenAI):
    area_id = state.area_id
    message_content = normalize_content(state.messages[-1].content)

    last_area_msg = db.LifeAreaMessage(
        id=new_id(),
        data=message_content,
        area_id=area_id,
        created_ts=get_timestamp(),
    )
    db.LifeAreaMessagesManager.create(last_area_msg.id, last_area_msg)

    area_msgs: list[str] = [
        msg.data for msg in db.LifeAreaMessagesManager.list_by_area(area_id)
    ]
    area_criteria: list[str] = [
        c.title for c in db.CriteriaManager.list_by_area(area_id)
    ]

    ai_answer, was_covered = await check_criteria_covered(area_msgs, area_criteria, llm)
    if was_covered:
        await state.extract_data_tasks.put(area_id)

    logger.info(
        "Interview criteria evaluated",
        extra={
            "area_id": str(area_id),
            "message_count": len(area_msgs),
            "criteria_count": len(area_criteria),
            "was_covered": was_covered,
        },
    )

    ai_msg = AIMessage(content=ai_answer)
    return {
        "messages": [ai_msg],
        "messages_to_save": {get_timestamp(): [ai_msg]},
        "success": True,
        "was_covered": was_covered,
    }


async def check_criteria_covered(
    interview_messages: list[str],
    area_criteria: list[str],
    llm: ChatOpenAI,
) -> tuple[str, bool]:
    system_prompt = (
        "You are an interview agent.\n"
        "Your task:\n"
        "1. If NO criteria exist yet → ask the user to create at least one criterion before proceeding\n"
        "2. Decide for EACH criterion whether it is clearly covered by the interview\n"
        "3. If ALL criteria are covered → thank the interviewee and close politely\n"
        "4. If NOT all covered → ask about ONE uncovered criterion (the most logical next one)\n\n"
        "Rules:\n"
        "- Be strict: unclear or partial answers = NOT covered\n"
        "- Ask only ONE question\n"
        "- Be polite, natural, and conversational\n"
    )

    user_prompt = {
        "interview_messages": interview_messages,
        "criteria": area_criteria,
    }

    structured_llm = llm.with_structured_output(CriteriaCoverageResult)

    result = await structured_llm.ainvoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_prompt)},
        ]
    )

    if not isinstance(result, CriteriaCoverageResult):
        result = CriteriaCoverageResult.model_validate(result)

    final_answer = result.final_answer
    all_covered = result.all_covered

    return final_answer, all_covered
