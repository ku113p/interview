"""Extract worker that processes extract tasks in background."""

import asyncio
import logging

from src.application.workers.channels import Channels
from src.config.settings import MAX_TOKENS_STRUCTURED, MODEL_EXTRACT_DATA
from src.infrastructure.ai import NewAI
from src.workflows.subgraphs.extract_data.graph import build_extract_data_graph
from src.workflows.subgraphs.extract_data.state import ExtractDataState

logger = logging.getLogger(__name__)


def _build_extract_graph():
    """Build the extract data graph with configured LLM."""
    return build_extract_data_graph(
        NewAI(MODEL_EXTRACT_DATA, max_tokens=MAX_TOKENS_STRUCTURED).build()
    )


async def _process_extract_task(task, graph, worker_id: int) -> None:
    """Process a single extract task."""
    extra = {
        "area_id": str(task.area_id),
        "user_id": str(task.user_id),
        "worker_id": worker_id,
    }
    logger.info("Processing extract task", extra=extra)
    state = ExtractDataState(area_id=task.area_id, user_id=task.user_id)
    await graph.ainvoke(state)
    logger.info("Completed extract task", extra=extra)


async def _worker_loop(worker_id: int, graph, channels: Channels) -> None:
    """Single worker loop processing tasks from queue."""
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


def create_extract_worker(channels: Channels):
    """Create an extract worker function for the pool.

    Returns a function that takes worker_id and runs the worker loop.
    """
    graph = _build_extract_graph()

    async def worker(worker_id: int) -> None:
        await _worker_loop(worker_id, graph, channels)

    return worker
