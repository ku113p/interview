import logging

from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from src.application.state import State
from src.config.settings import HISTORY_LIMIT_INTERVIEW, INPUT_TOKENS_INTERVIEW
from src.shared.prompts import build_interview_response_prompt
from src.shared.retry import invoke_with_retry
from src.shared.timestamp import get_timestamp
from src.shared.tokens import trim_messages_to_budget

logger = logging.getLogger(__name__)


async def interview_response(state: State, llm: ChatOpenAI):
    """Generate conversational response with history context."""
    if not state.criteria_analysis:
        raise ValueError(
            "interview_response requires criteria_analysis from previous node"
        )
    analysis = state.criteria_analysis

    covered_count = len([c for c in analysis.criteria if c.covered])
    total_count = len(analysis.criteria)

    system_prompt = build_interview_response_prompt(
        covered_count=covered_count,
        total_count=total_count,
        next_uncovered=analysis.next_uncovered,
    )

    # Filter out tool-related messages (area management artifacts)
    # These can cause "No tool call found" errors when ToolMessage appears
    # without its corresponding AIMessage with tool_calls
    chat_messages = [
        m
        for m in state.messages
        if not isinstance(m, ToolMessage)
        and not (isinstance(m, AIMessage) and getattr(m, "tool_calls", None))
    ]
    history = chat_messages[-HISTORY_LIMIT_INTERVIEW:]
    history = trim_messages_to_budget(history, INPUT_TOKENS_INTERVIEW)

    messages = [SystemMessage(content=system_prompt), *history]
    response = await invoke_with_retry(lambda: llm.ainvoke(messages))

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
