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
    PROMPT_SUMMARY_EVALUATE,
    PROMPT_TURN_SUMMARY,
)
from src.shared.retry import invoke_with_retry
from src.shared.timestamp import get_timestamp
from src.shared.tree_utils import SubAreaInfo, get_leaf_path
from src.shared.utils.content import normalize_content
from src.workflows.subgraphs.leaf_interview.helpers import build_leaf_history
from src.workflows.subgraphs.leaf_interview.state import LeafInterviewState

logger = logging.getLogger(__name__)


def _get_leaf_areas(sub_area_info: list[SubAreaInfo]) -> list[SubAreaInfo]:
    """Filter to only leaf areas (no children)."""
    all_ids = {info.area.id for info in sub_area_info}
    parent_ids = {info.area.parent_id for info in sub_area_info if info.area.parent_id}
    return [info for info in sub_area_info if info.area.id in (all_ids - parent_ids)]


async def _get_next_uncovered_leaf(
    area_id: uuid.UUID, exclude_id: uuid.UUID | None = None
) -> db.LifeArea | None:
    """Find next uncovered leaf using depth-first traversal.

    Traverses the area tree depth-first, returning the first leaf
    (area with no children) where covered_at IS NULL.

    exclude_id: skip this leaf even if covered_at is NULL (used for
    the just-completed leaf before its covered_at is persisted).
    """

    async def _traverse(current_id: uuid.UUID) -> db.LifeArea | None:
        children = await db.LifeAreasManager.get_descendants(current_id)
        # Only immediate children (parent_id == current_id)
        immediate = [c for c in children if c.parent_id == current_id]
        uncovered = [
            c for c in immediate if c.covered_at is None and c.id != exclude_id
        ]
        uncovered.sort(key=lambda x: str(x.id))

        for child in uncovered:
            grandchildren = [c for c in children if c.parent_id == child.id]
            if grandchildren:
                result = await _traverse(child.id)
                if result:
                    return result
            else:
                return child
        return None

    return await _traverse(area_id)


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


def _build_leaf_state(leaf: db.LifeArea | None, extra: dict | None = None) -> dict:
    """Build state dict for a leaf (or None if all done)."""
    if leaf is None:
        return {
            "all_leaves_done": True,
            "active_leaf_id": None,
            **(extra or {}),
        }
    return {
        "active_leaf_id": leaf.id,
        "question_text": None,
        "all_leaves_done": False,
        **(extra or {}),
    }


# --- Main Node Functions ---


async def load_interview_context(state: LeafInterviewState):
    """Load interview context using depth-first leaf traversal (stateless)."""
    area_id = state.area_id
    try:
        area = await db.LifeAreasManager.get_by_id(area_id)
        if area is not None and area.extracted_at is not None:
            logger.info("Area already extracted", extra={"area_id": str(area_id)})
            return {
                "area_already_extracted": True,
                "all_leaves_done": True,
                "active_leaf_id": None,
            }

        next_leaf = await _get_next_uncovered_leaf(area_id)
        if next_leaf is None:
            logger.info("All leaves covered", extra={"area_id": str(area_id)})
            return _build_leaf_state(None)

        logger.info("Loaded next leaf", extra={"leaf_id": str(next_leaf.id)})
        return _build_leaf_state(next_leaf)
    except Exception:
        logger.exception(
            "Failed to load interview context",
            extra={"area_id": str(area_id)},
        )
        return _build_leaf_state(None)


async def _get_question_text(state: LeafInterviewState) -> str:
    """Get the last AI question for the current leaf from history."""
    leaf_messages = await db.LeafHistoryManager.get_messages(state.active_leaf_id)
    question_text = state.question_text or "Initial question about this topic"
    for msg in reversed(leaf_messages):
        if msg.get("role") == "ai":
            question_text = msg.get("content", question_text)
            break
    return question_text


async def _invoke_turn_summary(
    llm: ChatOpenAI, leaf_path: str, question_text: str, user_message: str
) -> str:
    """Call LLM to generate a turn summary. Returns empty string if off-topic."""
    prompt = PROMPT_TURN_SUMMARY.format(
        leaf_path=leaf_path,
        question_text=question_text,
        user_message=user_message,
    )
    messages = [SystemMessage(content=prompt), HumanMessage(content="Extract summary.")]
    response = await invoke_with_retry(lambda: llm.ainvoke(messages))
    return normalize_content(response.content).strip()


async def create_turn_summary(state: LeafInterviewState, llm: ChatOpenAI):
    """Generate summary for this conversation turn (deferred write).

    Returns turn_summary_text in state — saved to DB in save_history.
    Returns empty dict if message is not relevant to the interview topic.
    """
    if not state.active_leaf_id or state.all_leaves_done:
        return {}

    current_messages = filter_tool_messages(state.messages)
    human_messages = [m for m in current_messages if isinstance(m, HumanMessage)]
    if not human_messages:
        return {}

    user_message = normalize_content(human_messages[-1].content)
    question_text = await _get_question_text(state)
    leaf_path = await get_leaf_path(state.active_leaf_id, state.area_id)
    summary_text = await _invoke_turn_summary(
        llm, leaf_path, question_text, user_message
    )

    if not summary_text:
        logger.info(
            "No summary extracted (off-topic turn)",
            extra={"leaf_id": str(state.active_leaf_id)},
        )
        return {}

    logger.info(
        "Generated turn summary",
        extra={"leaf_id": str(state.active_leaf_id), "length": len(summary_text)},
    )
    return {"turn_summary_text": summary_text}


async def _evaluate_with_summaries(
    state: LeafInterviewState, llm: ChatOpenAI
) -> LeafEvaluation:
    """Evaluate coverage using accumulated summaries."""
    summaries = await db.SummariesManager.list_by_area(state.active_leaf_id)

    if not summaries and not state.turn_summary_text:
        return LeafEvaluation(status="partial", reason="First turn, no summaries yet")

    summary_texts = [s.summary_text for s in summaries]
    if state.turn_summary_text:
        summary_texts.append(state.turn_summary_text)

    aggregated = "\n\n".join(summary_texts)
    leaf_path = await get_leaf_path(state.active_leaf_id, state.area_id)
    prompt = PROMPT_SUMMARY_EVALUATE.format(
        leaf_path=leaf_path,
        summaries=aggregated,
    )
    structured_llm = llm.with_structured_output(LeafEvaluation)
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Evaluate coverage."},
    ]
    result = await invoke_with_retry(lambda: structured_llm.ainvoke(messages))
    if not isinstance(result, LeafEvaluation):
        result = LeafEvaluation.model_validate(result)
    return result


async def quick_evaluate(state: LeafInterviewState, llm: ChatOpenAI):
    """Evaluate if user has fully answered the current leaf topic using summaries."""
    if state.all_leaves_done or not state.active_leaf_id:
        return {"leaf_evaluation": None, "is_successful": True}

    try:
        result = await _evaluate_with_summaries(state, llm)
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


async def update_coverage_status(state: LeafInterviewState, llm: ChatOpenAI):
    """Signal covered_at when leaf is complete or skipped (deferred write)."""
    if state.all_leaves_done or not state.active_leaf_id:
        return {"is_successful": True}

    evaluation = state.leaf_evaluation
    if evaluation and evaluation.status in ("complete", "skipped"):
        logger.info(
            "Leaf ready for completion",
            extra={"leaf_id": str(state.active_leaf_id), "status": evaluation.status},
        )
        return {"completed_leaf_id": state.active_leaf_id, "set_covered_at": True}
    return {}


async def _find_next_leaf(state: LeafInterviewState) -> dict:
    """Find next uncovered leaf and return in state. No DB writes.

    Passes completed_leaf_id as exclude_id so we skip the just-completed
    leaf even before its covered_at is persisted.
    """
    leaf_id = state.active_leaf_id
    completed_leaf_path = (
        await get_leaf_path(leaf_id, state.area_id) if leaf_id else None
    )

    next_leaf = await _get_next_uncovered_leaf(
        state.area_id, exclude_id=state.completed_leaf_id
    )

    if not next_leaf:
        logger.info("All leaves completed", extra={"area_id": str(state.area_id)})
        return _build_leaf_state(
            None,
            {"completed_leaf_path": completed_leaf_path, "is_fully_covered": True},
        )

    logger.info("Moving to next leaf", extra={"new_leaf_id": str(next_leaf.id)})
    return _build_leaf_state(next_leaf, {"completed_leaf_path": completed_leaf_path})


async def select_next_leaf(state: LeafInterviewState):
    """Select the next leaf to ask about, or stay on current if partial.

    Returns next leaf in state without DB writes.
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
