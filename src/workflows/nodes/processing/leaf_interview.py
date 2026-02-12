"""Leaf interview nodes - focused interview flow asking one leaf at a time."""

import json
import logging
import uuid

from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.infrastructure.db import managers as db
from src.processes.interview import State
from src.shared.ids import new_id
from src.shared.interview_models import LeafEvaluation
from src.shared.messages import filter_tool_messages, load_message_texts
from src.shared.prompts import (
    PROMPT_ALL_LEAVES_DONE,
    PROMPT_LEAF_COMPLETE,
    PROMPT_LEAF_FOLLOWUP,
    PROMPT_LEAF_QUESTION,
    PROMPT_QUICK_EVALUATE,
)
from src.shared.retry import invoke_with_retry
from src.shared.timestamp import get_timestamp
from src.shared.tree_utils import SubAreaInfo, build_sub_area_info
from src.shared.utils.content import normalize_content

logger = logging.getLogger(__name__)

_MIN_MESSAGES_FOR_CONTEXT = 2


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


async def _prompt_llm(llm: ChatOpenAI, prompt: str, user_msg: str) -> str:
    """Send prompt to LLM and return response content."""
    messages = [SystemMessage(content=prompt), {"role": "user", "content": user_msg}]
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
            "active_leaf_path": None,
            **(extra or {}),
        }
    return {
        "active_leaf_id": leaf.area.id,
        "active_leaf_path": leaf.path,
        "accumulated_message_ids": [],
        "question_text": None,
        "all_leaves_done": False,
        **(extra or {}),
    }


async def _create_leaf_context(
    user_id: uuid.UUID, area_id: uuid.UUID, leaf: SubAreaInfo
) -> None:
    """Create new interview context for a leaf."""
    now = get_timestamp()
    ctx = db.ActiveInterviewContext(
        user_id=user_id,
        root_area_id=area_id,
        active_leaf_id=leaf.area.id,
        created_at=now,
        message_ids=[],
    )
    await db.ActiveInterviewContextManager.create(user_id, ctx)
    await db.LeafCoverageManager.update_status(leaf.area.id, "active", now)


def _find_existing_context_state(
    context: db.ActiveInterviewContext, leaf_areas: list[SubAreaInfo]
) -> dict | None:
    """Check if existing context is valid and return state dict, or None."""
    for info in leaf_areas:
        if info.area.id == context.active_leaf_id:
            return {
                "active_leaf_id": context.active_leaf_id,
                "active_leaf_path": info.path,
                "accumulated_message_ids": context.message_ids or [],
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


async def load_interview_context(state: State):
    """Load or create active interview context for the user."""
    user_id, area_id = state.user.id, state.area_id
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


async def quick_evaluate(state: State, llm: ChatOpenAI):
    """Evaluate if user has fully answered the current leaf topic."""
    if state.all_leaves_done or not state.active_leaf_id:
        return {"leaf_evaluation": None}

    accumulated_texts = await load_message_texts(state.accumulated_message_ids)
    current_messages = filter_tool_messages(state.messages)
    if current_messages:
        accumulated_texts.append(
            f"User: {normalize_content(current_messages[-1].content)}"
        )

    prompt = PROMPT_QUICK_EVALUATE.format(
        leaf_path=state.active_leaf_path or "Unknown",
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
    logger.info(
        "Evaluation complete",
        extra={"leaf_id": str(state.active_leaf_id), "status": result.status},
    )
    return {"leaf_evaluation": result}


async def _save_user_message(state: State, current_messages: list) -> list[str]:
    """Save user message and return updated accumulated IDs."""
    current_text = normalize_content(current_messages[-1].content)
    message_text = f"User: {current_text}"
    if len(current_messages) >= _MIN_MESSAGES_FOR_CONTEXT and isinstance(
        current_messages[-2], AIMessage
    ):
        message_text = (
            f"AI: {normalize_content(current_messages[-2].content)}\n{message_text}"
        )

    msg_id = new_id()
    msg = db.LifeAreaMessage(
        id=msg_id,
        message_text=message_text,
        area_id=state.area_id,
        created_ts=get_timestamp(),
        leaf_ids=json.dumps([str(state.active_leaf_id)]),
    )
    await db.LifeAreaMessagesManager.create(msg_id, msg)

    accumulated = list(state.accumulated_message_ids or []) + [str(msg_id)]
    await db.ActiveInterviewContextManager.update_message_ids(
        state.user.id, accumulated
    )
    return accumulated


async def _mark_leaf_complete(
    state: State, evaluation: LeafEvaluation, accumulated: list[str]
) -> None:
    """Mark leaf as covered/skipped and queue extraction."""
    now = get_timestamp()
    status = "covered" if evaluation.status == "complete" else "skipped"
    await db.LeafCoverageManager.update_status(state.active_leaf_id, status, now)
    if evaluation.status == "complete":
        task = db.LeafExtractionQueueItem(
            id=new_id(),
            leaf_id=state.active_leaf_id,
            root_area_id=state.area_id,
            message_ids=accumulated,
            created_at=now,
        )
        await db.LeafExtractionQueueManager.create(task.id, task)
    logger.info(
        "Leaf marked as %s", status, extra={"leaf_id": str(state.active_leaf_id)}
    )


async def update_coverage_status(state: State):
    """Save the user's message and update coverage status."""
    if state.all_leaves_done or not state.active_leaf_id:
        return {}
    current_messages = filter_tool_messages(state.messages)
    if not current_messages:
        return {}

    accumulated = await _save_user_message(state, current_messages)
    evaluation = state.leaf_evaluation
    if evaluation and evaluation.status in ("complete", "skipped"):
        await _mark_leaf_complete(state, evaluation, accumulated)
    return {"accumulated_message_ids": accumulated}


async def select_next_leaf(state: State):
    """Select the next leaf to ask about, or stay on current if partial."""
    if state.all_leaves_done:
        return {}
    evaluation = state.leaf_evaluation
    if evaluation and evaluation.status == "partial":
        return {"all_leaves_done": False, "completed_leaf_path": None}

    completed_leaf_path = state.active_leaf_path
    leaf_areas = await _get_leaf_areas_for_root(state.area_id)
    next_leaf = await _get_next_uncovered_leaf(state.area_id, leaf_areas)

    if not next_leaf:
        await db.ActiveInterviewContextManager.delete_by_user(state.user.id)
        logger.info("All leaves completed", extra={"area_id": str(state.area_id)})
        return _build_leaf_state(
            None, {"completed_leaf_path": completed_leaf_path, "is_fully_covered": True}
        )

    now = get_timestamp()
    await db.ActiveInterviewContextManager.update_active_leaf(
        state.user.id, next_leaf.area.id, None
    )
    await db.LeafCoverageManager.update_status(next_leaf.area.id, "active", now)
    logger.info("Moving to next leaf", extra={"new_leaf_path": next_leaf.path})
    return _build_leaf_state(next_leaf, {"completed_leaf_path": completed_leaf_path})


async def _generate_response_content(
    state: State, llm: ChatOpenAI, current_leaf_path: str
) -> str:
    """Generate response content based on evaluation status."""
    evaluation = state.leaf_evaluation
    if evaluation and evaluation.status == "partial":
        accumulated_texts = await load_message_texts(state.accumulated_message_ids)
        prompt = PROMPT_LEAF_FOLLOWUP.format(
            leaf_path=current_leaf_path,
            accumulated_messages="\n\n".join(accumulated_texts)
            or "User provided partial answer",
            reason=evaluation.reason,
        )
        return await _prompt_llm(llm, prompt, "Ask a follow-up question.")
    if evaluation and evaluation.status in ("complete", "skipped"):
        completed_path = state.completed_leaf_path or current_leaf_path
        prompt = PROMPT_LEAF_COMPLETE.format(
            completed_leaf=completed_path, next_leaf=current_leaf_path
        )
        return await _prompt_llm(llm, prompt, "Generate transition.")
    return await _prompt_llm(
        llm,
        PROMPT_LEAF_QUESTION.format(leaf_path=current_leaf_path),
        "Ask the first question.",
    )


async def generate_leaf_response(state: State, llm: ChatOpenAI):
    """Generate a focused question or response for the current leaf."""
    if state.all_leaves_done:
        content = await _prompt_llm(
            llm, PROMPT_ALL_LEAVES_DONE, "Generate completion message."
        )
        return _build_response(AIMessage(content=content))

    current_leaf_path = state.active_leaf_path or "Unknown topic"
    content = await _generate_response_content(state, llm, current_leaf_path)
    ai_msg = AIMessage(content=content)
    question_text = normalize_content(content)

    if state.active_leaf_id:
        await db.ActiveInterviewContextManager.update_active_leaf(
            state.user.id, state.active_leaf_id, question_text
        )

    logger.info(
        "Generated response",
        extra={
            "leaf_path": current_leaf_path,
            "eval_status": state.leaf_evaluation.status
            if state.leaf_evaluation
            else "initial",
        },
    )
    return _build_response(ai_msg, question_text)
