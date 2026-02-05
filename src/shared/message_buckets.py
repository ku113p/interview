from __future__ import annotations

from langchain_core.messages import BaseMessage

# Type alias for timestamp -> messages mapping
MessageBuckets = dict[float, list[BaseMessage]]


def merge_message_buckets(
    left: MessageBuckets | None,
    right: MessageBuckets | None,
) -> MessageBuckets:
    """Merge two message bucket dictionaries, combining messages at same timestamps.

    Args:
        left: First message bucket or None
        right: Second message bucket or None

    Returns:
        MessageBuckets: Merged buckets
    """
    merged: MessageBuckets = {}
    for bucket in (left, right):
        if not bucket:
            continue
        for timestamp, messages in bucket.items():
            if timestamp in merged:
                merged[timestamp].extend(messages)
            else:
                merged[timestamp] = list(messages)
    return merged
