"""Message utilities for filtering and processing conversation history."""

import uuid

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage

__all__ = ["filter_tool_messages", "load_message_texts"]


def filter_tool_messages(messages: list[BaseMessage]) -> list[BaseMessage]:
    """Filter out tool-related messages for LLM calls without tools bound.

    Removes:
    - ToolMessage instances (tool execution results)
    - AIMessage instances that contain tool_calls (tool invocation requests)

    This is necessary when invoking LLMs without tools bound, as some providers
    (e.g., Azure OpenAI) reject requests containing tool-related messages.

    Args:
        messages: List of conversation messages to filter.

    Returns:
        Filtered list with tool-related messages removed.
    """
    return [
        msg
        for msg in messages
        if not isinstance(msg, ToolMessage)
        and not (isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None))
    ]


async def load_message_texts(message_ids: list[str] | None) -> list[str]:
    """Load message texts from IDs using a batch query.

    Args:
        message_ids: List of message ID strings, or None.

    Returns:
        List of message text strings in the same order as input IDs.
        Missing IDs are silently skipped.
    """
    if not message_ids:
        return []
    from src.infrastructure.db import managers as db

    uuids = [uuid.UUID(msg_id) for msg_id in message_ids]
    messages = await db.LifeAreaMessagesManager.get_by_ids(uuids)
    return [msg.message_text for msg in messages]
