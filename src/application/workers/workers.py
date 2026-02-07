"""Worker implementations and communication channels."""

import asyncio
import logging
import os
import tempfile
import uuid
from dataclasses import dataclass, field
from functools import partial

from src.application.graph import get_graph
from src.application.state import State, Target
from src.config.settings import MAX_TOKENS_STRUCTURED, MODEL_KNOWLEDGE_EXTRACTION
from src.domain import ClientMessage, User
from src.infrastructure.ai import NewAI
from src.infrastructure.db import repositories as db
from src.shared.ids import new_id
from src.shared.utils.content import normalize_content
from src.workflows.subgraphs.knowledge_extraction.graph import (
    build_knowledge_extraction_graph,
)
from src.workflows.subgraphs.knowledge_extraction.state import KnowledgeExtractionState

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Channels
# -----------------------------------------------------------------------------


@dataclass
class ExtractTask:
    """Task to extract data from an area for a user."""

    area_id: uuid.UUID
    user_id: uuid.UUID


@dataclass
class Channels:
    """Communication channels between CLI, graph worker, and extract worker."""

    client_message: asyncio.Queue[ClientMessage] = field(default_factory=asyncio.Queue)
    client_response: asyncio.Queue[str] = field(default_factory=asyncio.Queue)
    extract: asyncio.Queue[ExtractTask] = field(default_factory=asyncio.Queue)


# -----------------------------------------------------------------------------
# Graph Worker
# -----------------------------------------------------------------------------


def _build_state(msg: ClientMessage, user: User) -> tuple[State, list[str]]:
    """Build initial state for graph invocation.

    Returns:
        Tuple of (state, list of temp file paths to clean up)
    """
    media_tmp = tempfile.NamedTemporaryFile(delete=False)
    audio_tmp = tempfile.NamedTemporaryFile(delete=False)
    temp_files = [media_tmp.name, audio_tmp.name]

    # Close files so graph can use them
    media_tmp.close()
    audio_tmp.close()

    # Use current_area_id if set, otherwise generate a new one
    db_user = db.UsersManager.get_by_id(user.id)
    current_area_id = db_user.current_area_id if db_user is not None else None
    area_id = current_area_id if current_area_id is not None else new_id()

    # Extract text from message data
    text = msg.data if isinstance(msg.data, str) else ""

    state = State(
        user=user,
        message=msg,
        media_file=media_tmp.name,
        audio_file=audio_tmp.name,
        text=text,
        target=Target.interview,
        messages=[],
        messages_to_save={},
        success=None,
        area_id=area_id,
        was_covered=False,
    )
    return state, temp_files


def _format_response(messages: list[object]) -> str:
    """Extract response string from graph output messages."""
    if not messages:
        return "(no response)"
    return normalize_content(messages[-1].content) or "(no response)"


def _cleanup_tempfiles(temp_files: list[str]) -> None:
    """Delete temporary files."""
    for path in temp_files:
        try:
            os.unlink(path)
        except OSError:
            logger.debug("Failed to delete temp file %s", path)


async def _enqueue_extract_if_covered(
    result: dict, user: User, channels: Channels
) -> None:
    """Queue extract task if all criteria were covered."""
    if result.get("was_covered") and result.get("area_id"):
        task = ExtractTask(area_id=result["area_id"], user_id=user.id)
        await channels.extract.put(task)
        logger.info(
            "Queued extract task",
            extra={"area_id": str(task.area_id), "user_id": str(user.id)},
        )


async def _process_message(
    msg: ClientMessage, user: User, graph, channels: Channels
) -> None:
    """Process a single message through the graph."""
    state, temp_files = _build_state(msg, user)
    try:
        result = await graph.ainvoke(state)
        if not isinstance(result, dict):
            result = result.model_dump()

        response = _format_response(result.get("messages", []))
        await channels.client_response.put(response)
        await _enqueue_extract_if_covered(result, user, channels)
    finally:
        _cleanup_tempfiles(temp_files)


async def _graph_worker_loop(
    worker_id: int, graph, channels: Channels, user: User
) -> None:
    """Single graph worker loop processing messages from queue."""
    while True:
        msg = await channels.client_message.get()
        try:
            logger.debug("Graph worker %d processing message", worker_id)
            await _process_message(msg, user, graph, channels)
        except Exception:
            logger.exception("Graph worker %d error", worker_id)
            await channels.client_response.put("An error occurred")
        finally:
            channels.client_message.task_done()


# -----------------------------------------------------------------------------
# Extract Worker
# -----------------------------------------------------------------------------


def _build_knowledge_extraction_graph():
    """Build the knowledge extraction graph with configured LLM."""
    return build_knowledge_extraction_graph(
        NewAI(MODEL_KNOWLEDGE_EXTRACTION, max_tokens=MAX_TOKENS_STRUCTURED).build()
    )


async def _process_extract_task(task: ExtractTask, graph, worker_id: int) -> None:
    """Process a single extract task."""
    extra = {
        "area_id": str(task.area_id),
        "user_id": str(task.user_id),
        "worker_id": worker_id,
    }
    logger.info("Processing extract task", extra=extra)
    state = KnowledgeExtractionState(area_id=task.area_id, user_id=task.user_id)
    await graph.ainvoke(state)
    logger.info("Completed extract task", extra=extra)


async def _extract_worker_loop(worker_id: int, graph, channels: Channels) -> None:
    """Single extract worker loop processing tasks from queue."""
    while True:
        task = await channels.extract.get()
        try:
            await _process_extract_task(task, graph, worker_id)
        except asyncio.CancelledError:
            logger.info("Extract worker %d cancelled", worker_id)
            raise
        except Exception:
            logger.exception("Extract worker %d error", worker_id)
        finally:
            channels.extract.task_done()


def create_graph_worker(channels: Channels, user: User):
    """Create a graph worker function using partial application."""
    graph = get_graph()
    return partial(_graph_worker_loop, graph=graph, channels=channels, user=user)


def create_extract_worker(channels: Channels):
    """Create an extract worker function using partial application."""
    graph = _build_knowledge_extraction_graph()
    return partial(_extract_worker_loop, graph=graph, channels=channels)
