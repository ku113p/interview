"""Graph worker pool for processing messages through the main graph."""

import asyncio
import logging
import os
import tempfile
from functools import partial
from typing import Any

from src.config.settings import WORKER_POLL_TIMEOUT, WORKER_POOL_GRAPH
from src.domain import ClientMessage, InputMode, User
from src.infrastructure.db import managers as db
from src.processes.extract.interfaces import ExtractTask
from src.processes.interview.graph import get_graph
from src.processes.interview.interfaces import (
    ChannelRequest,
    ChannelResponse,
)
from src.processes.interview.state import State, Target
from src.runtime import Channels, run_worker_pool
from src.shared.ids import new_id
from src.shared.utils.content import normalize_content

logger = logging.getLogger(__name__)


async def _init_graph_state(msg: ClientMessage, user: User) -> tuple[State, list[str]]:
    """Initialize graph state and create temporary files for media processing."""
    media_tmp = tempfile.NamedTemporaryFile(delete=False)
    audio_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_files = [media_tmp.name, audio_tmp.name]
    media_tmp.close()
    audio_tmp.close()

    db_user = await db.UsersManager.get_by_id(user.id)
    current_area_id = db_user.current_area_id if db_user is not None else None
    area_id = current_area_id if current_area_id is not None else new_id()
    text = msg.data if isinstance(msg.data, str) else ""

    state = State(
        user=user,
        message=msg,
        media_file=media_tmp.name,
        audio_file=audio_tmp.name,
        text=text,
        target=Target.conduct_interview,
        messages=[],
        messages_to_save={},
        is_successful=None,
        area_id=area_id,
    )
    return state, temp_files


def _cleanup_tempfiles(temp_files: list[str]) -> None:
    """Delete temporary files, ignoring errors."""
    for path in temp_files:
        try:
            os.unlink(path)
        except OSError:
            logger.debug("Failed to delete temp file %s", path)


async def _enqueue_extract_if_summary_saved(result: dict, channels: Channels) -> None:
    """Queue extract task when a turn summary was saved."""
    summary_id = result.get("pending_summary_id")
    if summary_id:
        await channels.extract.put(ExtractTask(summary_id=summary_id))
        logger.info("Queued extract task", extra={"summary_id": str(summary_id)})


async def _get_user_from_db(user_id) -> User:
    """Look up user from database by ID."""
    db_user = await db.UsersManager.get_by_id(user_id)
    if db_user is None:
        raise ValueError(f"User {user_id} not found in database")
    return User(
        id=db_user.id,
        mode=InputMode(db_user.mode),
        current_life_area_id=db_user.current_area_id,
    )


async def _invoke_graph_and_get_response(
    msg: ClientMessage, user: User, graph, channels: Channels
) -> str:
    """Invoke the graph with a message and return the AI response."""
    state, temp_files = await _init_graph_state(msg, user)
    try:
        result = await graph.ainvoke(state)
        if not isinstance(result, dict):
            result = result.model_dump()
        messages: list[Any] = result.get("messages", [])
        response = normalize_content(messages[-1].content) if messages else ""
        await _enqueue_extract_if_summary_saved(result, channels)
        return response or "(no response)"
    finally:
        _cleanup_tempfiles(temp_files)


async def _process_channel_request(
    request: ChannelRequest, graph, channels: Channels, worker_id: int
) -> None:
    """Process a channel request: invoke graph and send response."""
    try:
        logger.debug("Graph worker %d processing message", worker_id)
        user = await _get_user_from_db(request.user_id)
        response = await _invoke_graph_and_get_response(
            request.client_message, user, graph, channels
        )
        await channels.responses.put(
            ChannelResponse(
                correlation_id=request.correlation_id, response_text=response
            )
        )
    except Exception:
        logger.exception("Graph worker %d error", worker_id)
        await channels.responses.put(
            ChannelResponse(
                correlation_id=request.correlation_id, response_text="An error occurred"
            )
        )


async def _graph_worker_loop(worker_id: int, graph, channels: Channels) -> None:
    """Process messages through the main graph."""
    while not channels.shutdown.is_set():
        try:
            request = await asyncio.wait_for(
                channels.requests.get(), timeout=WORKER_POLL_TIMEOUT
            )
        except asyncio.TimeoutError:
            continue
        try:
            await _process_channel_request(request, graph, channels, worker_id)
        finally:
            channels.requests.task_done()


async def run_graph_pool(channels: Channels) -> None:
    """Run the graph worker pool."""
    graph = get_graph()
    worker_fn = partial(_graph_worker_loop, graph=graph, channels=channels)
    await run_worker_pool("graph", worker_fn, WORKER_POOL_GRAPH, channels.shutdown)
