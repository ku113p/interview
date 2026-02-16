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
    leaf_summary_text: str | None = None
    leaf_completion_status: str | None = None  # "covered" or "skipped"


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


async def _save_messages(state: SaveHistoryState, conn) -> None:
    """Save message history and leaf-history links within a transaction."""
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
            elif state.active_leaf_id:
                await db.LeafHistoryManager.link(
                    state.active_leaf_id, history_id, conn=conn
                )


async def _save_leaf_completion(state: SaveHistoryState, conn, now: float) -> None:
    """Persist deferred leaf coverage status and summary within a transaction."""
    if not state.completed_leaf_id or not state.leaf_completion_status:
        return
    if state.leaf_summary_text is not None:
        await db.LeafCoverageManager.save_summary_text(
            state.completed_leaf_id, state.leaf_summary_text, now, conn=conn
        )
    await db.LeafCoverageManager.update_status(
        state.completed_leaf_id, state.leaf_completion_status, now, conn=conn
    )


async def _save_context_transition(state: SaveHistoryState, conn, now: float) -> None:
    """Persist interview context transition within a transaction.

    No-ops on partial evaluation turns (question_text is None) — the existing
    question_text in the DB from the previous turn remains valid.
    """
    if state.is_fully_covered:
        await db.ActiveInterviewContextManager.delete_by_user(state.user.id, conn=conn)
    elif state.active_leaf_id and state.question_text:
        await db.ActiveInterviewContextManager.update_active_leaf(
            state.user.id, state.active_leaf_id, state.question_text, conn=conn
        )
        # If transitioning to a new leaf, mark it active
        if state.completed_leaf_id and state.active_leaf_id != state.completed_leaf_id:
            await db.LeafCoverageManager.update_status(
                state.active_leaf_id, "active", now, conn=conn
            )


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
        await _save_messages(state, conn)
        await _save_leaf_completion(state, conn, now)
        await _save_context_transition(state, conn, now)

    return {}
