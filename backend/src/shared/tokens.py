"""Token estimation and context management utilities."""

from langchain_core.messages import BaseMessage

from src.shared.utils.content import normalize_content

# Approximate characters per token (conservative estimate)
CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    """Estimate token count using character-based approximation.

    Uses a conservative estimate of 4 characters per token.
    This is faster than using a tokenizer but less accurate.

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated token count
    """
    return len(text) // CHARS_PER_TOKEN


def estimate_message_tokens(message: BaseMessage) -> int:
    """Estimate token count for a single message.

    Args:
        message: Message to estimate tokens for

    Returns:
        Estimated token count
    """
    content = normalize_content(message.content)
    return estimate_tokens(content)


def trim_messages_to_budget(
    messages: list[BaseMessage],
    max_tokens: int,
) -> list[BaseMessage]:
    """Trim messages from the beginning to fit within token budget.

    Keeps the most recent messages while staying within the token budget.
    Always keeps at least the last message.

    Args:
        messages: List of messages to trim
        max_tokens: Maximum token budget

    Returns:
        Trimmed list of messages fitting within budget
    """
    if not messages:
        return []

    total_tokens = sum(estimate_message_tokens(m) for m in messages)

    if total_tokens <= max_tokens:
        return messages

    # Trim from beginning, keeping most recent
    trimmed: list[BaseMessage] = []
    remaining_budget = max_tokens

    for msg in reversed(messages):
        msg_tokens = estimate_message_tokens(msg)
        if msg_tokens <= remaining_budget:
            trimmed.insert(0, msg)
            remaining_budget -= msg_tokens
        elif not trimmed:
            # Always include at least the last message
            trimmed.insert(0, msg)
            break
        else:
            break

    return trimmed
