import logging

from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.config.settings import HISTORY_LIMIT_EXTRACT_TARGET
from src.processes.interview import State
from src.shared.messages import filter_tool_messages
from src.shared.prompts import PROMPT_SMALL_TALK
from src.shared.retry import invoke_with_retry
from src.shared.timestamp import get_timestamp

logger = logging.getLogger(__name__)


async def small_talk_response(state: State, llm: ChatOpenAI):
    """Generate response for greetings, app questions, and casual chat."""
    chat_messages = filter_tool_messages(state.messages)
    history = chat_messages[-HISTORY_LIMIT_EXTRACT_TARGET:]
    messages = [SystemMessage(content=PROMPT_SMALL_TALK), *history]

    response = await invoke_with_retry(lambda: llm.ainvoke(messages))

    logger.info(
        "Small talk response generated",
        extra={"history_length": len(history)},
    )

    ai_msg = AIMessage(content=response.content)
    return {
        "messages": [ai_msg],
        "messages_to_save": {get_timestamp(): [ai_msg]},
        "is_successful": True,
    }
