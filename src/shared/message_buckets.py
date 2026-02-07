from __future__ import annotations

from langchain_core.messages import BaseMessage

# Type alias for timestamp -> messages mapping
MessageBuckets = dict[float, list[BaseMessage]]


def merge_message_buckets(
    left: MessageBuckets | None,
    right: MessageBuckets | None,
) -> MessageBuckets:
    """Merge two message bucket dictionaries with deduplication.

    When subgraphs inherit parent state, the same message can appear in both
    parent and child buckets at the same timestamp. This function deduplicates
    by checking (message type, content) pairs.

    Args:
        left: First message bucket or None
        right: Second message bucket or None

    Returns:
        MessageBuckets: Merged buckets with duplicates removed
    """
    merged: MessageBuckets = {}

    for bucket in (left, right):
        if not bucket:
            continue
        for timestamp, messages in bucket.items():
            if timestamp not in merged:
                merged[timestamp] = []

            # Track seen (type, content) pairs for deduplication
            seen = {(m.type, str(m.content)) for m in merged[timestamp]}

            for msg in messages:
                key = (msg.type, str(msg.content))
                if key not in seen:
                    merged[timestamp].append(msg)
                    seen.add(key)

    return merged
