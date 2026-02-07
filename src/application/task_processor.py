"""Background task processor for extract_data tasks.

This module provides a reusable task processor that can be used by any adapter
(CLI, API, MCP) to process extract_data tasks in the background.
"""

import asyncio
import logging

from src.config.settings import MAX_TOKENS_STRUCTURED, MODEL_EXTRACT_DATA
from src.domain import ExtractDataTask
from src.infrastructure.ai import NewAI
from src.workflows.subgraphs.extract_data.graph import build_extract_data_graph
from src.workflows.subgraphs.extract_data.state import ExtractDataState

logger = logging.getLogger(__name__)


def build_extract_graph():
    """Build the extract data graph with configured LLM."""
    return build_extract_data_graph(
        NewAI(MODEL_EXTRACT_DATA, max_tokens=MAX_TOKENS_STRUCTURED).build()
    )


async def process_extract_task(extract_graph, task: ExtractDataTask) -> None:
    """Process a single extract_data task."""
    logger.info(
        "Processing extract_data task",
        extra={"area_id": str(task.area_id), "user_id": str(task.user_id)},
    )
    state = ExtractDataState(area_id=task.area_id, user_id=task.user_id)
    await extract_graph.ainvoke(state)
    logger.info(
        "Completed extract_data task",
        extra={"area_id": str(task.area_id), "user_id": str(task.user_id)},
    )


async def _process_queue_item(
    extract_graph, queue: asyncio.Queue[ExtractDataTask]
) -> bool:
    """Process one queue item. Returns False to stop the loop."""
    task = None
    try:
        task = await queue.get()
        await process_extract_task(extract_graph, task)
    except asyncio.CancelledError:
        logger.info("Extract data task processor cancelled")
        return False
    except Exception:
        logger.exception("Error processing extract_data task")
    finally:
        if task is not None:
            queue.task_done()
    return True


async def run_task_processor(queue: asyncio.Queue[ExtractDataTask]) -> None:
    """Background task processor for extract_data tasks.

    This function runs indefinitely, processing tasks from the queue.
    It should be run as an asyncio task and cancelled when shutting down.

    Args:
        queue: Queue of ExtractDataTask items to process
    """
    extract_graph = build_extract_graph()
    while await _process_queue_item(extract_graph, queue):
        pass
