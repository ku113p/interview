from __future__ import annotations

import hashlib
import json
from typing import Any

from langchain_core.messages import BaseMessage

# Type alias for timestamp -> messages mapping
MessageBuckets = dict[float, list[BaseMessage]]


def _serialize_json_safe(value: Any) -> str:
    """Serialize value to JSON string, falling back to str() on error."""
    try:
        return json.dumps(value, sort_keys=True)
    except (TypeError, ValueError):
        return str(value)


def _serialize_content(content: str | list | Any) -> str:
    """Serialize message content for hashing."""
    if isinstance(content, str):
        return content
    return _serialize_json_safe(content)


def _get_tool_key_parts(msg: BaseMessage) -> list[str]:
    """Get key parts from tool-related message attributes."""
    parts = []
    tool_calls = getattr(msg, "tool_calls", None)
    if tool_calls:
        parts.append(_serialize_json_safe(tool_calls))
    tool_call_id = getattr(msg, "tool_call_id", None)
    if tool_call_id:
        parts.append(str(tool_call_id))
    return parts


def _compute_message_key(msg: BaseMessage) -> str:
    """Compute a stable hash key for message deduplication."""
    key_parts = [msg.type, _serialize_content(msg.content)]
    key_parts.extend(_get_tool_key_parts(msg))
    combined = "|".join(key_parts)
    return hashlib.sha256(combined.encode()).hexdigest()


def merge_message_buckets(
    left: MessageBuckets | None,
    right: MessageBuckets | None,
) -> MessageBuckets:
    """Merge two message bucket dictionaries with deduplication.

    When subgraphs inherit parent state, the same message can appear in both
    parent and child buckets at the same timestamp. This function deduplicates
    by computing a stable hash of each message.

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

            # Track seen message hashes for deduplication
            seen = {_compute_message_key(m) for m in merged[timestamp]}

            for msg in messages:
                key = _compute_message_key(msg)
                if key not in seen:
                    merged[timestamp].append(msg)
                    seen.add(key)

    return merged
