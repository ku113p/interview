"""Message utilities for filtering and processing conversation history."""

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage

__all__ = ["filter_tool_messages"]


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
