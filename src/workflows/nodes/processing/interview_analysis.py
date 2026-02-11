import asyncio
import json
import logging

from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI

from src.infrastructure.db import managers as db
from src.processes.interview import State
from src.shared.ids import new_id
from src.shared.interview_models import AreaCoverageAnalysis
from src.shared.prompts import PROMPT_INTERVIEW_ANALYSIS
from src.shared.retry import invoke_with_retry
from src.shared.timestamp import get_timestamp
from src.shared.tree_utils import build_sub_area_info, build_tree_text
from src.shared.utils.content import normalize_content

logger = logging.getLogger(__name__)

# Need at least 2 messages to have a preceding AI question before user answer
_MIN_MESSAGES_FOR_CONTEXT = 2


def _format_qa_data(messages: list[BaseMessage]) -> str:
    """Format user answer with preceding AI question for sub-area coverage context."""
    user_content = normalize_content(messages[-1].content)

    # Include preceding AI question so LLM understands what user was responding to
    has_preceding_message = len(messages) >= _MIN_MESSAGES_FOR_CONTEXT
    if has_preceding_message and isinstance(messages[-2], AIMessage):
        ai_content = normalize_content(messages[-2].content)
        return f"AI: {ai_content}\nUser: {user_content}"

    return f"User: {user_content}"


async def interview_analysis(state: State, llm: ChatOpenAI):
    """Analyze sub-area coverage without generating response."""
    area_id = state.area_id

    # Check if area was already extracted
    area = await db.LifeAreasManager.get_by_id(area_id)
    if area is not None and area.extracted_at is not None:
        return {"area_already_extracted": True}

    # Prepare message for saving (but don't save yet - wait for successful analysis)
    current_message_text = _format_qa_data(state.messages)

    # Get existing area data and descendants in parallel
    messages_result, sub_area_objects = await asyncio.gather(
        db.LifeAreaMessagesManager.list_by_area(area_id),
        db.LifeAreasManager.get_descendants(area_id),
    )
    area_messages: list[str] = [msg.message_text for msg in messages_result]

    # Build tree text for LLM context
    tree_text = build_tree_text(sub_area_objects, area_id)

    # Build paths for unambiguous structured output
    sub_area_info = build_sub_area_info(sub_area_objects, area_id)
    sub_area_paths = [info.path for info in sub_area_info]

    # Include current message in analysis (even though not yet saved)
    messages_for_analysis = area_messages + [current_message_text]

    # Analyze coverage with tree context
    analysis = await _analyze_sub_area_coverage(
        messages_for_analysis, sub_area_paths, tree_text, llm
    )

    # Save message only after successful analysis
    last_area_msg = db.LifeAreaMessage(
        id=new_id(),
        message_text=current_message_text,
        area_id=area_id,
        created_ts=get_timestamp(),
    )
    await db.LifeAreaMessagesManager.create(last_area_msg.id, last_area_msg)

    logger.info(
        "Interview sub-areas analyzed",
        extra={
            "area_id": str(area_id),
            "message_count": len(area_messages),
            "sub_area_count": len(sub_area_paths),
            "all_covered": analysis.all_covered,
            "next_uncovered": analysis.next_uncovered,
        },
    )

    return {
        "coverage_analysis": analysis,
        "is_fully_covered": analysis.all_covered,
    }


async def _analyze_sub_area_coverage(
    interview_messages: list[str],
    sub_area_paths: list[str],
    tree_text: str,
    llm: ChatOpenAI,
) -> AreaCoverageAnalysis:
    """Analyze which sub-areas are covered by the collected messages."""
    user_prompt = {
        "interview_messages": interview_messages,
        "sub_areas_tree": tree_text,
        "sub_area_paths": sub_area_paths,
    }

    structured_llm = llm.with_structured_output(AreaCoverageAnalysis)
    messages = [
        {"role": "system", "content": PROMPT_INTERVIEW_ANALYSIS},
        {"role": "user", "content": json.dumps(user_prompt)},
    ]

    result = await invoke_with_retry(lambda: structured_llm.ainvoke(messages))

    if not isinstance(result, AreaCoverageAnalysis):
        result = AreaCoverageAnalysis.model_validate(result)

    return result
