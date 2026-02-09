import json
import logging

from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI

from src.application.state import State
from src.infrastructure.db import managers as db
from src.shared.ids import new_id
from src.shared.interview_models import CriteriaAnalysis
from src.shared.prompts import PROMPT_INTERVIEW_ANALYSIS
from src.shared.retry import invoke_with_retry
from src.shared.timestamp import get_timestamp
from src.shared.utils.content import normalize_content

logger = logging.getLogger(__name__)

# Need at least 2 messages to have a preceding AI question before user answer
_MIN_MESSAGES_FOR_CONTEXT = 2


def _format_qa_data(messages: list[BaseMessage]) -> str:
    """Format user answer with preceding AI question for criteria coverage context."""
    user_content = normalize_content(messages[-1].content)

    # Include preceding AI question so LLM understands what user was responding to
    has_preceding_message = len(messages) >= _MIN_MESSAGES_FOR_CONTEXT
    if has_preceding_message and isinstance(messages[-2], AIMessage):
        ai_content = normalize_content(messages[-2].content)
        return f"AI: {ai_content}\nUser: {user_content}"

    return f"User: {user_content}"


async def interview_analysis(state: State, llm: ChatOpenAI):
    """Analyze criteria coverage without generating response."""
    area_id = state.area_id

    # Save answer with question context for criteria coverage analysis
    last_area_msg = db.LifeAreaMessage(
        id=new_id(),
        message_text=_format_qa_data(state.messages),
        area_id=area_id,
        created_ts=get_timestamp(),
    )
    await db.LifeAreaMessagesManager.create(last_area_msg.id, last_area_msg)

    # Get area data
    area_messages: list[str] = [
        message.message_text
        for message in await db.LifeAreaMessagesManager.list_by_area(area_id)
    ]
    area_criteria: list[str] = [
        criterion.title for criterion in await db.CriteriaManager.list_by_area(area_id)
    ]

    # Analyze coverage (structured output)
    analysis = await _analyze_criteria_coverage(area_messages, area_criteria, llm)

    logger.info(
        "Interview criteria analyzed",
        extra={
            "area_id": str(area_id),
            "message_count": len(area_messages),
            "criteria_count": len(area_criteria),
            "all_covered": analysis.all_covered,
            "next_uncovered": analysis.next_uncovered,
        },
    )

    return {
        "criteria_analysis": analysis,
        "is_fully_covered": analysis.all_covered,
    }


async def _analyze_criteria_coverage(
    interview_messages: list[str],
    area_criteria: list[str],
    llm: ChatOpenAI,
) -> CriteriaAnalysis:
    """Analyze which interview criteria are covered by the collected messages."""
    user_prompt = {
        "interview_messages": interview_messages,
        "criteria": area_criteria,
    }

    structured_llm = llm.with_structured_output(CriteriaAnalysis)
    messages = [
        {"role": "system", "content": PROMPT_INTERVIEW_ANALYSIS},
        {"role": "user", "content": json.dumps(user_prompt)},
    ]

    result = await invoke_with_retry(lambda: structured_llm.ainvoke(messages))

    if not isinstance(result, CriteriaAnalysis):
        result = CriteriaAnalysis.model_validate(result)

    return result
