import asyncio
import logging
import uuid
from typing import Annotated

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from pydantic import BaseModel, ConfigDict

from src.config.settings import HISTORY_LIMIT_INTERVIEW
from src.shared.interview_models import CriteriaAnalysis
from src.shared.message_buckets import MessageBuckets, merge_message_buckets
from src.shared.timestamp import get_timestamp

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


async def interview_response(state: State, llm: ChatOpenAI):
    """Generate conversational response with history context."""
    if not state.criteria_analysis:
        raise ValueError(
            "interview_response requires criteria_analysis from previous node"
        )
    analysis = state.criteria_analysis

    covered_count = len([c for c in analysis.criteria if c.covered])
    total_count = len(analysis.criteria)

    system_prompt = (
        "You are a friendly interview assistant.\n"
        "Based on the analysis provided, respond naturally:\n"
        f"- Criteria status: {covered_count}/{total_count} covered\n"
        f"- Next topic: {analysis.next_uncovered or 'All covered!'}\n\n"
        "Rules:\n"
        "- Do NOT repeat greetings if conversation has already started\n"
        "- If no criteria exist: gently mention that no criteria are defined yet and suggest creating some\n"
        "- If all criteria covered: thank them and close politely\n"
        "- If criteria remain: ask about the next uncovered topic\n"
        "- Ask only ONE question at a time\n"
        "- Be polite, natural, and conversational\n"
    )

    # Follow area_chat pattern - use conversation history
    history = state.messages[-HISTORY_LIMIT_INTERVIEW:]

    response = await llm.ainvoke([SystemMessage(content=system_prompt), *history])

    logger.info(
        "Interview response generated",
        extra={
            "area_id": str(state.area_id),
            "history_length": len(history),
            "covered_count": covered_count,
            "total_count": total_count,
        },
    )

    ai_msg = AIMessage(content=response.content)
    return {
        "messages": [ai_msg],
        "messages_to_save": {get_timestamp(): [ai_msg]},
        "success": True,
    }
