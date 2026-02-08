import json
import logging

from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI

from src.application.state import State
from src.infrastructure.db import repositories as db
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
        data=_format_qa_data(state.messages),
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
