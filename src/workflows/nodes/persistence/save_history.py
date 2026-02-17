import logging
import uuid
from typing import Annotated

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from pydantic import BaseModel

from src.domain.models import User
from src.infrastructure.db import managers as db
from src.shared.ids import new_id
from src.shared.message_buckets import MessageBuckets, merge_message_buckets
from src.shared.timestamp import get_timestamp
from src.shared.utils.content import normalize_content

logger = logging.getLogger(__name__)


class SaveHistoryState(BaseModel):
    user: User
    messages_to_save: Annotated[MessageBuckets, merge_message_buckets]
    is_successful: bool | None = None
    active_leaf_id: uuid.UUID | None = None
    completed_leaf_id: uuid.UUID | None = None  # Leaf just marked complete
    question_text: str | None = None
    is_fully_covered: bool = False

    # Deferred DB write data from subgraph nodes
    turn_summary_text: str | None = None  # Per-turn summary text
    set_covered_at: bool = False  # Signal to set covered_at on completed leaf


def _normalize_role(role: str) -> str:
    if role == "human":
        return "user"
    if role == "ai":
        return "ai"
    if role == "tool":
        return "tool"
    logger.warning("Unexpected message role '%s', defaulting to 'ai'", role)
    return "ai"


def _message_to_dict(msg: BaseMessage) -> dict[str, object]:
    role = getattr(msg, "type", None) or msg.__class__.__name__.lower()
    content = normalize_content(msg.content)
    data: dict[str, object] = {"role": _normalize_role(str(role)), "content": content}
    if isinstance(msg, AIMessage):
        tool_calls = getattr(msg, "tool_calls", None)
        if tool_calls:
            data["tool_calls"] = tool_calls
    if isinstance(msg, ToolMessage):
        data["tool_call_id"] = str(msg.tool_call_id)
        if msg.name:
            data["name"] = msg.name
    return data


async def _save_messages(state: SaveHistoryState, conn) -> uuid.UUID | None:
    """Save message history and leaf-history links within a transaction.

    Returns the history_id of the human (answer) message if any.
    """
    answer_id: uuid.UUID | None = None
    for created_ts, messages in state.messages_to_save.items():
        for msg in messages:
            history_id = new_id()
            await db.HistoriesManager.create(
                history_id,
                db.History(
                    id=history_id,
                    message_data=_message_to_dict(msg),
                    user_id=state.user.id,
                    created_ts=created_ts,
                ),
                conn=conn,
                auto_commit=False,
            )
            # User's answer → link to completed_leaf_id (the leaf they answered about)
            # AI's next question → link to active_leaf_id (the next leaf)
            if state.completed_leaf_id and isinstance(msg, HumanMessage):
                await db.LeafHistoryManager.link(
                    state.completed_leaf_id, history_id, conn=conn
                )
                answer_id = history_id
            elif state.active_leaf_id:
                await db.LeafHistoryManager.link(
                    state.active_leaf_id, history_id, conn=conn
                )
    return answer_id


async def _save_turn_summary(
    state: SaveHistoryState,
    conn,
    now: float,
    answer_id: uuid.UUID | None = None,
) -> uuid.UUID | None:
    """Save turn summary if present (deferred write from create_turn_summary).

    Returns the created summary_id, or None if no summary was saved.
    """
    if not state.turn_summary_text:
        return None

    leaf_id = state.completed_leaf_id or state.active_leaf_id
    if not leaf_id:
        return None

    question_id: uuid.UUID | None = None
    messages_with_ids = await db.LeafHistoryManager.get_messages_with_ids(
        leaf_id, conn=conn
    )
    for msg_id, msg in reversed(messages_with_ids):
        if msg.get("role") in ("ai", "assistant"):
            question_id = msg_id
            break

    summary_id = await db.SummariesManager.create_summary(
        area_id=leaf_id,
        summary_text=state.turn_summary_text,
        created_at=now,
        question_id=question_id,
        answer_id=answer_id,
        conn=conn,
    )
    logger.info("Saved turn summary", extra={"leaf_id": str(leaf_id)})
    return summary_id


async def _save_leaf_completion(state: SaveHistoryState, conn, now: float) -> None:
    """Set covered_at when leaf is complete or skipped."""
    if not state.completed_leaf_id or not state.set_covered_at:
        return

    await db.LifeAreasManager.set_covered_at(state.completed_leaf_id, now, conn=conn)
    logger.info("Set covered_at", extra={"leaf_id": str(state.completed_leaf_id)})


async def save_history(state: SaveHistoryState) -> dict:
    messages_by_ts = state.messages_to_save or {}
    if not messages_by_ts:
        logger.debug("No messages to save", extra={"user_id": str(state.user.id)})
        return {}

    message_count = sum(len(messages) for messages in messages_by_ts.values())
    logger.info(
        "Saving history",
        extra={"user_id": str(state.user.id), "count": message_count},
    )

    from src.infrastructure.db.connection import transaction

    now = get_timestamp()
    async with transaction() as conn:
        answer_id = await _save_messages(state, conn)
        summary_id = await _save_turn_summary(state, conn, now, answer_id=answer_id)
        await _save_leaf_completion(state, conn, now)

    result: dict = {}
    if summary_id:
        result["pending_summary_id"] = summary_id
    return result
