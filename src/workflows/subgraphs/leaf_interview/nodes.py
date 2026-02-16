"""Leaf interview nodes - focused interview flow asking one leaf at a time."""

import logging
import uuid

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.config.settings import HISTORY_LIMIT_EXTRACT_TARGET
from src.infrastructure.db import managers as db
from src.shared.interview_models import LeafEvaluation
from src.shared.messages import filter_tool_messages
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
from src.workflows.subgraphs.leaf_interview.helpers import (
    accumulate_with_current,
    build_leaf_history,
    format_history_messages,
)
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
    area_id: uuid.UUID,
    leaf_areas: list[SubAreaInfo],
    exclude_ids: set[uuid.UUID] | None = None,
) -> SubAreaInfo | None:
    """Get first uncovered leaf.

    Args:
        area_id: Root area ID.
        leaf_areas: All leaf areas for the root.
        exclude_ids: Leaf IDs to skip (e.g. just-completed leaf whose
            status hasn't been persisted yet).
    """
    coverage_list = await db.LeafCoverageManager.list_by_root_area(area_id)
    covered_ids = {
        lc.leaf_id for lc in coverage_list if lc.status in ("covered", "skipped")
    }
    skip_ids = covered_ids | (exclude_ids or set())
    for info in leaf_areas:
        if info.area.id not in skip_ids:
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
        await db.LeafCoverageManager.update_status(
            leaf.area.id, "active", now, conn=conn
        )


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


async def _check_early_exit(
    area_id: uuid.UUID,
) -> tuple[dict | None, list[SubAreaInfo]]:
    """Return (early_state, leaf_areas) — early_state is set if we should bail."""
    area = await db.LifeAreasManager.get_by_id(area_id)
    if area is not None and area.extracted_at is not None:
        logger.info("Area already extracted", extra={"area_id": str(area_id)})
        return {"area_already_extracted": True, **_build_leaf_state(None)}, []
    leaf_areas = await _get_leaf_areas_for_root(area_id)
    if not leaf_areas:
        logger.info("No leaf areas found", extra={"area_id": str(area_id)})
        return _build_leaf_state(None), []
    return None, leaf_areas


async def _load_or_create_context(user_id: uuid.UUID, area_id: uuid.UUID) -> dict:
    """Load existing context or create new one for the user."""
    early, leaf_areas = await _check_early_exit(area_id)
    if early is not None:
        return early

    context = await db.ActiveInterviewContextManager.get_by_user(user_id)
    if context and context.root_area_id == area_id:
        existing = _find_existing_context_state(context, leaf_areas)
        if existing:
            cov = await db.LeafCoverageManager.get_by_id(context.active_leaf_id)
            if not cov or cov.status not in ("covered", "skipped"):
                logger.info("Loaded existing context", extra={"user_id": str(user_id)})
                return existing
            logger.info(
                "Active leaf already covered, advancing",
                extra={"leaf_id": str(context.active_leaf_id)},
            )

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


async def _evaluate_leaf_response(
    state: LeafInterviewState, llm: ChatOpenAI, leaf_messages: list[dict]
) -> LeafEvaluation:
    """Run LLM evaluation on accumulated messages."""
    current_messages = filter_tool_messages(state.messages)
    accumulated_texts = accumulate_with_current(leaf_messages, current_messages)
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

    try:
        result = await _evaluate_leaf_response(state, llm, leaf_messages)
    except Exception:
        logger.exception(
            "Failed to evaluate leaf response",
            extra={"leaf_id": str(state.active_leaf_id)},
        )
        return {
            "leaf_evaluation": LeafEvaluation(
                status="partial", reason="Evaluation failed"
            )
        }
    logger.info(
        "Evaluation complete",
        extra={"leaf_id": str(state.active_leaf_id), "status": result.status},
    )
    return {"leaf_evaluation": result}


async def _extract_leaf_summary(
    state: LeafInterviewState, llm: ChatOpenAI
) -> str | None:
    """Extract a summary of the user's responses for this leaf."""
    leaf_messages = await db.LeafHistoryManager.get_messages(state.active_leaf_id)

    # Add current user message not yet in history
    current_messages = filter_tool_messages(state.messages)
    message_texts = format_history_messages(leaf_messages)
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


async def _prepare_leaf_completion(
    state: LeafInterviewState, evaluation: LeafEvaluation, llm: ChatOpenAI
) -> dict:
    """Compute leaf completion data without writing to DB.

    Returns state dict with summary/status for deferred persistence.
    """
    status = "covered" if evaluation.status == "complete" else "skipped"
    result: dict = {"leaf_completion_status": status}

    if status == "covered":
        summary = await _extract_leaf_summary(state, llm)
        if summary is not None:
            result["leaf_summary_text"] = summary
            logger.info(
                "Prepared leaf summary",
                extra={
                    "leaf_id": str(state.active_leaf_id),
                    "summary_len": len(summary),
                },
            )

    logger.info(
        "Leaf prepared as %s", status, extra={"leaf_id": str(state.active_leaf_id)}
    )
    return result


async def update_coverage_status(state: LeafInterviewState, llm: ChatOpenAI):
    """Compute coverage data for deferred persistence.

    Returns completion data in state instead of writing to DB.
    Actual DB writes happen in save_history for atomicity.
    """
    if state.all_leaves_done or not state.active_leaf_id:
        return {"is_successful": True}

    evaluation = state.leaf_evaluation
    if evaluation and evaluation.status in ("complete", "skipped"):
        completion_data = await _prepare_leaf_completion(state, evaluation, llm)
        return {"completed_leaf_id": state.active_leaf_id, **completion_data}
    return {}


async def _find_next_leaf(state: LeafInterviewState) -> dict:
    """Find next uncovered leaf and return in state. No DB writes.

    Passes exclude_ids so the just-completed leaf (whose status hasn't been
    persisted yet) is skipped.
    """
    leaf_id = state.active_leaf_id
    completed_leaf_path = (
        await get_leaf_path(leaf_id, state.area_id) if leaf_id else None
    )
    leaf_areas = await _get_leaf_areas_for_root(state.area_id)
    exclude = {leaf_id} if leaf_id else None
    next_leaf = await _get_next_uncovered_leaf(state.area_id, leaf_areas, exclude)

    if not next_leaf:
        logger.info("All leaves completed", extra={"area_id": str(state.area_id)})
        return _build_leaf_state(
            None,
            {"completed_leaf_path": completed_leaf_path, "is_fully_covered": True},
        )

    logger.info("Moving to next leaf", extra={"new_leaf_path": next_leaf.path})
    return _build_leaf_state(next_leaf, {"completed_leaf_path": completed_leaf_path})


async def select_next_leaf(state: LeafInterviewState):
    """Select the next leaf to ask about, or stay on current if partial.

    Returns next leaf in state without DB writes. Actual transitions
    happen in save_history for atomicity.
    """
    if state.all_leaves_done:
        return {"is_successful": True}
    if state.leaf_evaluation and state.leaf_evaluation.status == "partial":
        return {"all_leaves_done": False, "completed_leaf_path": None}

    try:
        return await _find_next_leaf(state)
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
        history = build_leaf_history(leaf_messages, current_messages)
        prompt = PROMPT_LEAF_FOLLOWUP.format(
            leaf_path=current_leaf_path, reason=evaluation.reason
        )
        return await _prompt_llm_with_history(llm, prompt, history)
    if evaluation and evaluation.status in ("complete", "skipped"):
        completed_path = state.completed_leaf_path or current_leaf_path
        prompt = PROMPT_LEAF_COMPLETE.format(
            completed_leaf=completed_path, next_leaf=current_leaf_path
        )
        # Don't include history - prevents contamination from previous topic
        return await _prompt_llm_with_history(llm, prompt, [])
    prompt = PROMPT_LEAF_QUESTION.format(leaf_path=current_leaf_path)
    return await _prompt_llm_with_history(llm, prompt, current_messages[-8:])


async def generate_leaf_response(state: LeafInterviewState, llm: ChatOpenAI):
    """Generate a focused question or response for the current leaf.

    Returns question_text in state for deferred persistence in save_history.
    Bails out if a prior node (e.g. select_next_leaf) signalled failure.
    """
    if state.is_successful is False:
        return {}

    leaf_path = "Unknown topic"
    if state.active_leaf_id:
        leaf_path = await get_leaf_path(state.active_leaf_id, state.area_id)

    content = await _generate_response_content(state, llm, leaf_path)
    question_text = normalize_content(content) if not state.all_leaves_done else None

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
