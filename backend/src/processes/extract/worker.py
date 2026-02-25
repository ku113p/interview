"""Extract worker pool for knowledge extraction from summaries."""

import asyncio
import logging
from functools import partial

from src.config.settings import (
    MAX_TOKENS_KNOWLEDGE,
    MODEL_KNOWLEDGE_EXTRACTION,
    WORKER_POLL_TIMEOUT,
    WORKER_POOL_EXTRACT,
)
from src.infrastructure.ai import LLMClientBuilder
from src.processes.extract.interfaces import ExtractTask
from src.runtime import Channels, run_worker_pool
from src.workflows.subgraphs.knowledge_extraction.graph import (
    build_knowledge_extraction_graph,
)
from src.workflows.subgraphs.knowledge_extraction.state import KnowledgeExtractionState

logger = logging.getLogger(__name__)


async def _invoke_extraction_graph(task: ExtractTask, graph, worker_id: int) -> None:
    """Invoke the knowledge extraction graph for a task."""
    extra = {"summary_id": str(task.summary_id), "worker_id": worker_id}
    logger.info("Processing extract task", extra=extra)
    state = KnowledgeExtractionState(summary_id=task.summary_id)
    await graph.ainvoke(state)
    logger.info("Completed extract task", extra=extra)


async def _run_extraction_with_recovery(
    task: ExtractTask,
    graph,
    channels: Channels,
    worker_id: int,
) -> None:
    """Run extraction with error recovery - log and continue on failure."""
    try:
        await _invoke_extraction_graph(task, graph, worker_id)
    except asyncio.CancelledError:
        logger.info("Extract worker %d cancelled", worker_id)
        raise
    except Exception:
        logger.exception("Extract worker %d error", worker_id)


async def _extract_worker_loop(worker_id: int, graph, channels: Channels) -> None:
    """Process knowledge extraction tasks."""
    while not channels.shutdown.is_set():
        try:
            task = await asyncio.wait_for(
                channels.extract.get(), timeout=WORKER_POLL_TIMEOUT
            )
        except asyncio.TimeoutError:
            continue
        try:
            await _run_extraction_with_recovery(task, graph, channels, worker_id)
        finally:
            channels.extract.task_done()


async def run_extract_pool(channels: Channels) -> None:
    """Run the extract worker pool."""
    # Minimize reasoning for structured output to avoid LengthFinishReasonError
    graph = build_knowledge_extraction_graph(
        LLMClientBuilder(
            MODEL_KNOWLEDGE_EXTRACTION,
            max_tokens=MAX_TOKENS_KNOWLEDGE,
            reasoning={"effort": "low"},
        ).build()
    )
    worker_fn = partial(_extract_worker_loop, graph=graph, channels=channels)
    await run_worker_pool("extract", worker_fn, WORKER_POOL_EXTRACT, channels.shutdown)
