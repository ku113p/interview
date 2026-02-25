"""Helper functions for leaf interview nodes."""

from langchain_core.messages import AIMessage, HumanMessage

from src.shared.messages import format_role
from src.shared.utils.content import normalize_content


def format_history_messages(messages: list[dict]) -> list[str]:
    """Format history message dicts as text strings."""
    texts = []
    for msg in messages:
        role = format_role(msg.get("role", "unknown"))
        content = msg.get("content", "")
        texts.append(f"{role}: {content}")
    return texts


def accumulate_with_current(
    leaf_messages: list[dict], current_messages: list
) -> list[str]:
    """Build accumulated texts from history messages plus current user message."""
    texts = format_history_messages(leaf_messages)
    if current_messages:
        texts.append(f"User: {normalize_content(current_messages[-1].content)}")
    return texts


def build_leaf_history(leaf_messages: list[dict], current_messages: list) -> list:
    """Build chat history from leaf messages plus current user message only."""
    history = []
    for msg in leaf_messages:
        role, content = msg.get("role", ""), msg.get("content", "")
        if role in ("user", "human"):
            history.append(HumanMessage(content=content))
        elif role in ("assistant", "ai"):
            history.append(AIMessage(content=content))

    # Only add the latest user message if not already in history
    if current_messages:
        latest = current_messages[-1]
        if latest.content not in {msg.content for msg in history}:
            history.append(latest)

    return history
