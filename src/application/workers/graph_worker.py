"""Graph worker that processes client messages and produces responses."""

import logging
import os
import tempfile
import uuid

from langchain_core.messages import BaseMessage

from src.application.graph import get_graph
from src.application.state import State, Target
from src.application.workers.channels import Channels, ExtractTask
from src.domain import ClientMessage, User
from src.infrastructure.db import repositories as db
from src.shared.ids import new_id
from src.shared.utils.content import normalize_content

logger = logging.getLogger(__name__)


def _get_current_area_id(user_id: uuid.UUID) -> uuid.UUID | None:
    """Get user's current_area_id from database."""
    db_user = db.UsersManager.get_by_id(user_id)
    if db_user is not None:
        return db_user.current_area_id
    return None


def _format_response(messages: list[BaseMessage]) -> str:
    """Extract response string from graph output messages."""
    if not messages:
        return "(no response)"
    last_msg = messages[-1]
    return normalize_content(last_msg.content) or "(no response)"


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
    current_area_id = _get_current_area_id(user.id)
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


async def _worker_loop(worker_id: int, graph, channels: Channels, user: User) -> None:
    """Single worker loop processing messages from queue."""
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


def create_graph_worker(channels: Channels, user: User):
    """Create a graph worker function for the pool.

    Returns a function that takes worker_id and runs the worker loop.
    """
    graph = get_graph()

    async def worker(worker_id: int) -> None:
        await _worker_loop(worker_id, graph, channels, user)

    return worker
