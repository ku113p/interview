"""Leaf interview nodes - focused interview flow asking one leaf at a time."""

import logging
import uuid

from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.config.settings import HISTORY_LIMIT_EXTRACT_TARGET
from src.infrastructure.db import managers as db
from src.shared.interview_models import LeafEvaluation
from src.shared.messages import filter_tool_messages, format_role
from src.shared.prompts import (
    PROMPT_ALL_LEAVES_DONE,
    PROMPT_COMPLETED_AREA,
    PROMPT_LEAF_COMPLETE,
    PROMPT_LEAF_FOLLOWUP,
    PROMPT_LEAF_QUESTION,
    PROMPT_LEAF_SUMMARY,
    PROMPT_QUICK_EVALUATE,
)
from src.shared.retry import invoke_with_retry
from src.shared.timestamp import get_timestamp
from src.shared.tree_utils import SubAreaInfo, build_sub_area_info, get_leaf_path
from src.shared.utils.content import normalize_content
from src.workflows.subgraphs.leaf_interview.state import LeafInterviewState

logger = logging.getLogger(__name__)


def _get_leaf_areas(sub_area_info: list[SubAreaInfo]) -> list[SubAreaInfo]:
    """Filter to only leaf areas (no children)."""
    all_ids = {info.area.id for info in sub_area_info}
    parent_ids = {info.area.parent_id for info in sub_area_info if info.area.parent_id}
    return [info for info in sub_area_info if info.area.id in (all_ids - parent_ids)]


async def _get_leaf_areas_for_root(area_id: uuid.UUID) -> list[SubAreaInfo]:
    """Get leaf areas for a root area, creating coverage records if needed."""
    descendants = await db.LifeAreasManager.get_descendants(area_id)
    leaf_areas = _get_leaf_areas(build_sub_area_info(descendants, area_id))
    if leaf_areas:
        await _ensure_coverage_records(area_id, leaf_areas)
    return leaf_areas


async def _ensure_coverage_records(
    area_id: uuid.UUID, leaf_areas: list[SubAreaInfo]
) -> None:
    """Create missing coverage records."""
    existing = await db.LeafCoverageManager.list_by_root_area(area_id)
    existing_ids = {lc.leaf_id for lc in existing}
    now = get_timestamp()
    for info in leaf_areas:
        if info.area.id not in existing_ids:
            coverage = db.LeafCoverage(
                leaf_id=info.area.id,
                root_area_id=area_id,
                status="pending",
                updated_at=now,
            )
            await db.LeafCoverageManager.create(info.area.id, coverage)


async def _get_next_uncovered_leaf(
    area_id: uuid.UUID, leaf_areas: list[SubAreaInfo]
) -> SubAreaInfo | None:
    """Get first uncovered leaf."""
    coverage_list = await db.LeafCoverageManager.list_by_root_area(area_id)
    covered_ids = {
        lc.leaf_id for lc in coverage_list if lc.status in ("covered", "skipped")
    }
    for info in leaf_areas:
        if info.area.id not in covered_ids:
            return info
    return None


async def _prompt_llm_with_history(llm: ChatOpenAI, prompt: str, history: list) -> str:
    """Send system prompt + chat history to LLM and return response content."""
    messages = [SystemMessage(content=prompt), *history]
    response = await invoke_with_retry(lambda: llm.ainvoke(messages))
    return response.content


def _build_response(ai_msg: AIMessage, question_text: str | None = None) -> dict:
    """Build standard node response with AI message."""
    result = {
        "messages": [ai_msg],
        "messages_to_save": {get_timestamp(): [ai_msg]},
        "is_successful": True,
    }
    if question_text:
        result["question_text"] = question_text
    return result


def _build_leaf_state(leaf: SubAreaInfo | None, extra: dict | None = None) -> dict:
    """Build state dict for a leaf (or None if all done)."""
    if leaf is None:
        return {
            "all_leaves_done": True,
            "active_leaf_id": None,
            **(extra or {}),
        }
    return {
        "active_leaf_id": leaf.area.id,
        "question_text": None,
        "all_leaves_done": False,
        **(extra or {}),
    }


async def _create_leaf_context(
    user_id: uuid.UUID, area_id: uuid.UUID, leaf: SubAreaInfo
) -> None:
    """Create new interview context for a leaf."""
    from src.infrastructure.db.connection import transaction

    now = get_timestamp()
    ctx = db.ActiveInterviewContext(
        user_id=user_id,
        root_area_id=area_id,
        active_leaf_id=leaf.area.id,
        created_at=now,
    )
    async with transaction() as conn:
        await db.ActiveInterviewContextManager.create(user_id, ctx, conn=conn)
        await db.LeafCoverageManager.update_status(leaf.area.id, "active", now, conn)


def _find_existing_context_state(
    context: db.ActiveInterviewContext, leaf_areas: list[SubAreaInfo]
) -> dict | None:
    """Check if existing context is valid and return state dict, or None."""
    for info in leaf_areas:
        if info.area.id == context.active_leaf_id:
            return {
                "active_leaf_id": context.active_leaf_id,
                "question_text": context.question_text,
                "all_leaves_done": False,
            }
    return None


# --- Main Node Functions ---


async def _handle_no_next_leaf(
    context: db.ActiveInterviewContext | None, area_id: uuid.UUID
) -> dict:
    """Handle case when no uncovered leaf remains."""
    if context:
        await db.ActiveInterviewContextManager.delete_by_user(context.user_id)
    logger.info("All leaves covered", extra={"area_id": str(area_id)})
    return _build_leaf_state(None)


async def _load_or_create_context(user_id: uuid.UUID, area_id: uuid.UUID) -> dict:
    """Load existing context or create new one for the user."""
    leaf_areas = await _get_leaf_areas_for_root(area_id)
    if not leaf_areas:
        logger.info("No leaf areas found", extra={"area_id": str(area_id)})
        return _build_leaf_state(None)

    context = await db.ActiveInterviewContextManager.get_by_user(user_id)
    if context and context.root_area_id == area_id:
        existing = _find_existing_context_state(context, leaf_areas)
        if existing:
            logger.info("Loaded existing context", extra={"user_id": str(user_id)})
            return existing

    next_leaf = await _get_next_uncovered_leaf(area_id, leaf_areas)
    if not next_leaf:
        return await _handle_no_next_leaf(context, area_id)

    await _create_leaf_context(user_id, area_id, next_leaf)
    logger.info("Created new context", extra={"leaf_path": next_leaf.path})
    return _build_leaf_state(next_leaf)


async def load_interview_context(state: LeafInterviewState):
    """Load or create active interview context for the user."""
    user_id, area_id = state.user.id, state.area_id
    try:
        return await _load_or_create_context(user_id, area_id)
    except Exception:
        logger.exception(
            "Failed to load interview context",
            extra={"user_id": str(user_id), "area_id": str(area_id)},
        )
        return _build_leaf_state(None)


def _format_history_messages(messages: list[dict]) -> list[str]:
    """Format history message dicts as text strings."""
    texts = []
    for msg in messages:
        role = format_role(msg.get("role", "unknown"))
        content = msg.get("content", "")
        texts.append(f"{role}: {content}")
    return texts


def _accumulate_with_current(
    leaf_messages: list[dict], current_messages: list
) -> list[str]:
    """Build accumulated texts from history messages plus current user message."""
    texts = _format_history_messages(leaf_messages)
    if current_messages:
        texts.append(f"User: {normalize_content(current_messages[-1].content)}")
    return texts


def _build_leaf_history(
    leaf_messages: list[dict], current_messages: list, context_limit: int = 8
) -> list:
    """Build chat history from leaf messages plus recent conversation context."""
    from langchain_core.messages import AIMessage, HumanMessage

    history = []
    for msg in leaf_messages:
        role, content = msg.get("role", ""), msg.get("content", "")
        if role in ("user", "human"):
            history.append(HumanMessage(content=content))
        elif role in ("assistant", "ai"):
            history.append(AIMessage(content=content))
    if current_messages:
        existing_content = {msg.content for msg in history}
        for msg in current_messages[-context_limit:]:
            if msg.content not in existing_content:
                history.append(msg)
                existing_content.add(msg.content)
    return history


async def _evaluate_leaf_response(
    state: LeafInterviewState, llm: ChatOpenAI, leaf_messages: list[dict]
) -> LeafEvaluation:
    """Run LLM evaluation on accumulated messages."""
    current_messages = filter_tool_messages(state.messages)
    accumulated_texts = _accumulate_with_current(leaf_messages, current_messages)
    leaf_path = await get_leaf_path(state.active_leaf_id, state.area_id)
    prompt = PROMPT_QUICK_EVALUATE.format(
        leaf_path=leaf_path,
        question_text=state.question_text or "Initial question about this topic",
        accumulated_messages="\n\n".join(accumulated_texts) or "No messages yet",
    )
    structured_llm = llm.with_structured_output(LeafEvaluation)
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Evaluate the response."},
    ]
    result = await invoke_with_retry(lambda: structured_llm.ainvoke(messages))
    if not isinstance(result, LeafEvaluation):
        result = LeafEvaluation.model_validate(result)
    return result


async def quick_evaluate(state: LeafInterviewState, llm: ChatOpenAI):
    """Evaluate if user has fully answered the current leaf topic."""
    if state.all_leaves_done or not state.active_leaf_id:
        return {"leaf_evaluation": None, "is_successful": True}

    try:
        leaf_messages = await db.LeafHistoryManager.get_messages(state.active_leaf_id)
    except Exception:
        logger.exception(
            "Failed to get leaf messages for evaluation",
            extra={"leaf_id": str(state.active_leaf_id)},
        )
        return {"leaf_evaluation": None, "is_successful": True}

    result = await _evaluate_leaf_response(state, llm, leaf_messages)
    logger.info(
        "Evaluation complete",
        extra={"leaf_id": str(state.active_leaf_id), "status": result.status},
    )
    return {"leaf_evaluation": result}


async def _extract_leaf_summary(
    state: LeafInterviewState, llm: ChatOpenAI
) -> str | None:
    """Extract a summary of the user's responses for this leaf."""
    from langchain_core.messages import HumanMessage

    leaf_messages = await db.LeafHistoryManager.get_messages(state.active_leaf_id)
    if not leaf_messages:
        return None

    # Add current user message not yet in history
    current_messages = filter_tool_messages(state.messages)
    message_texts = _format_history_messages(leaf_messages)
    if current_messages:
        message_texts.append(f"User: {normalize_content(current_messages[-1].content)}")

    if not message_texts:
        return None

    leaf_path = await get_leaf_path(state.active_leaf_id, state.area_id)
    prompt = PROMPT_LEAF_SUMMARY.format(
        leaf_path=leaf_path,
        messages="\n\n".join(message_texts),
    )
    messages = [SystemMessage(content=prompt), HumanMessage(content="Extract summary.")]
    response = await invoke_with_retry(lambda: llm.ainvoke(messages))
    return normalize_content(response.content)


async def _save_leaf_summary(
    state: LeafInterviewState, llm: ChatOpenAI, now: float
) -> None:
    """Extract and save summary for a covered leaf. Errors are logged and suppressed."""
    from src.infrastructure.embeddings import get_embedding_client

    summary = await _extract_leaf_summary(state, llm)
    if not summary:
        return
    embed_client = get_embedding_client()
    vector = await invoke_with_retry(lambda: embed_client.aembed_query(summary))
    await db.LeafCoverageManager.save_summary(
        state.active_leaf_id, summary, vector, now
    )
    logger.info(
        "Saved leaf summary",
        extra={"leaf_id": str(state.active_leaf_id), "summary_len": len(summary)},
    )


async def _mark_leaf_complete(
    state: LeafInterviewState, evaluation: LeafEvaluation, llm: ChatOpenAI
) -> None:
    """Mark leaf as covered/skipped and extract summary if covered."""
    now = get_timestamp()
    status = "covered" if evaluation.status == "complete" else "skipped"

    if status == "covered":
        try:
            await _save_leaf_summary(state, llm, now)
        except Exception:
            logger.exception(
                "Failed to extract leaf summary",
                extra={"leaf_id": str(state.active_leaf_id)},
            )

    await db.LeafCoverageManager.update_status(state.active_leaf_id, status, now)
    logger.info(
        "Leaf marked as %s", status, extra={"leaf_id": str(state.active_leaf_id)}
    )


async def update_coverage_status(state: LeafInterviewState, llm: ChatOpenAI):
    """Update coverage status based on evaluation.

    Extracts and saves a summary when a leaf is marked complete, then returns
    completed_leaf_id so the worker can queue extraction.
    """
    if state.all_leaves_done or not state.active_leaf_id:
        return {"is_successful": True}

    evaluation = state.leaf_evaluation
    if evaluation and evaluation.status in ("complete", "skipped"):
        await _mark_leaf_complete(state, evaluation, llm)
        return {"completed_leaf_id": state.active_leaf_id}
    return {}


async def _transition_to_next_leaf(user_id: uuid.UUID, next_leaf: SubAreaInfo) -> None:
    """Update DB to transition to the next leaf in a transaction."""
    from src.infrastructure.db.connection import transaction

    now = get_timestamp()
    async with transaction() as conn:
        await db.ActiveInterviewContextManager.update_active_leaf(
            user_id, next_leaf.area.id, None, conn=conn
        )
        await db.LeafCoverageManager.update_status(
            next_leaf.area.id, "active", now, conn=conn
        )


async def _find_and_transition_to_next(state: LeafInterviewState) -> dict:
    """Find next uncovered leaf and transition to it, or mark all done."""
    leaf_id = state.active_leaf_id
    completed_leaf_path = (
        await get_leaf_path(leaf_id, state.area_id) if leaf_id else None
    )
    leaf_areas = await _get_leaf_areas_for_root(state.area_id)
    next_leaf = await _get_next_uncovered_leaf(state.area_id, leaf_areas)

    if not next_leaf:
        await db.ActiveInterviewContextManager.delete_by_user(state.user.id)
        logger.info("All leaves completed", extra={"area_id": str(state.area_id)})
        return _build_leaf_state(
            None,
            {"completed_leaf_path": completed_leaf_path, "is_fully_covered": True},
        )

    await _transition_to_next_leaf(state.user.id, next_leaf)
    logger.info("Moving to next leaf", extra={"new_leaf_path": next_leaf.path})
    return _build_leaf_state(next_leaf, {"completed_leaf_path": completed_leaf_path})


async def select_next_leaf(state: LeafInterviewState):
    """Select the next leaf to ask about, or stay on current if partial."""
    if state.all_leaves_done:
        return {"is_successful": True}
    if state.leaf_evaluation and state.leaf_evaluation.status == "partial":
        return {"all_leaves_done": False, "completed_leaf_path": None}

    try:
        return await _find_and_transition_to_next(state)
    except Exception:
        logger.exception(
            "Failed to select next leaf",
            extra={"area_id": str(state.area_id), "user_id": str(state.user.id)},
        )
        return {"is_successful": False}


async def _generate_response_content(
    state: LeafInterviewState, llm: ChatOpenAI, current_leaf_path: str
) -> str:
    """Generate response content based on evaluation status."""
    current_messages = filter_tool_messages(state.messages)
    if state.all_leaves_done:
        return await _prompt_llm_with_history(
            llm, PROMPT_ALL_LEAVES_DONE, current_messages[-8:]
        )
    evaluation = state.leaf_evaluation
    if evaluation and evaluation.status == "partial":
        leaf_messages = await db.LeafHistoryManager.get_messages(state.active_leaf_id)
        history = _build_leaf_history(leaf_messages, current_messages)
        prompt = PROMPT_LEAF_FOLLOWUP.format(
            leaf_path=current_leaf_path, reason=evaluation.reason
        )
        return await _prompt_llm_with_history(llm, prompt, history)
    if evaluation and evaluation.status in ("complete", "skipped"):
        completed_path = state.completed_leaf_path or current_leaf_path
        prompt = PROMPT_LEAF_COMPLETE.format(
            completed_leaf=completed_path, next_leaf=current_leaf_path
        )
        return await _prompt_llm_with_history(llm, prompt, current_messages[-8:])
    prompt = PROMPT_LEAF_QUESTION.format(leaf_path=current_leaf_path)
    return await _prompt_llm_with_history(llm, prompt, current_messages[-8:])


async def _update_leaf_context(user_id: uuid.UUID, leaf_id: uuid.UUID, text: str):
    """Update active leaf context, logging errors without raising."""
    try:
        await db.ActiveInterviewContextManager.update_active_leaf(
            user_id, leaf_id, text
        )
    except Exception:
        logger.exception(
            "Failed to update leaf context", extra={"leaf_id": str(leaf_id)}
        )


async def generate_leaf_response(state: LeafInterviewState, llm: ChatOpenAI):
    """Generate a focused question or response for the current leaf."""
    leaf_path = "Unknown topic"
    if state.active_leaf_id:
        leaf_path = await get_leaf_path(state.active_leaf_id, state.area_id)

    content = await _generate_response_content(state, llm, leaf_path)
    question_text = normalize_content(content) if not state.all_leaves_done else None

    if state.active_leaf_id and question_text:
        await _update_leaf_context(state.user.id, state.active_leaf_id, question_text)

    eval_status = state.leaf_evaluation.status if state.leaf_evaluation else "initial"
    logger.info(
        "Generated response", extra={"leaf_path": leaf_path, "eval_status": eval_status}
    )
    return _build_response(AIMessage(content=content), question_text)


async def completed_area_response(state: LeafInterviewState, llm: ChatOpenAI):
    """Generate response for already-extracted areas."""
    prompt = PROMPT_COMPLETED_AREA.format(area_id=str(state.area_id))
    chat_messages = filter_tool_messages(state.messages)
    history = chat_messages[-HISTORY_LIMIT_EXTRACT_TARGET:]
    messages = [SystemMessage(content=prompt), *history]

    response = await invoke_with_retry(lambda: llm.ainvoke(messages))

    logger.info(
        "Completed area response generated",
        extra={"area_id": str(state.area_id)},
    )

    ai_msg = AIMessage(content=response.content)
    return {
        "messages": [ai_msg],
        "messages_to_save": {get_timestamp(): [ai_msg]},
        "is_successful": True,
    }
