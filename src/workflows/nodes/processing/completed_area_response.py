"""Response node for already-extracted areas."""

import logging

from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.config.settings import HISTORY_LIMIT_EXTRACT_TARGET
from src.processes.interview import State
from src.shared.retry import invoke_with_retry
from src.shared.timestamp import get_timestamp

logger = logging.getLogger(__name__)

PROMPT_COMPLETED_AREA = """You are a helpful interview assistant.

The user is talking about a topic that has already been fully documented and extracted.

Politely acknowledge what they said, then explain:
1. This area has already been completed and insights were extracted
2. If they want to add new information, they can reset this area using the command shown below
3. Resetting will remove the extracted knowledge so they can re-do the interview

Be conversational and helpful. Include the reset command at the end.

Reset command: /reset-area_{area_id}
"""


async def completed_area_response(state: State, llm: ChatOpenAI):
    """Generate response for already-extracted areas."""
    prompt = PROMPT_COMPLETED_AREA.format(area_id=str(state.area_id))
    history = state.messages[-HISTORY_LIMIT_EXTRACT_TARGET:]
    messages = [SystemMessage(content=prompt), *history]

    response = await invoke_with_retry(lambda: llm.ainvoke(messages))

    logger.info(
        "Completed area response generated",
        extra={"area_id": str(state.area_id)},
    )

    ai_msg = AIMessage(content=response.content)
    return {
        "messages": [ai_msg],
        "messages_to_save": {get_timestamp(): [ai_msg]},
        "is_successful": True,
    }
