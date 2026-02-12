"""Leaf extraction worker - extracts summaries from completed leaf interviews."""

import asyncio
import logging
import uuid

from langchain_openai import ChatOpenAI

from src.config.settings import (
    LEAF_EXTRACT_BATCH_SIZE,
    LEAF_EXTRACT_MAX_RETRIES,
    LEAF_EXTRACT_POLL_INTERVAL,
    WORKER_POOL_LEAF_EXTRACT,
)
from src.infrastructure.db import managers as db
from src.infrastructure.embeddings import get_embedding_client
from src.infrastructure.llms import get_llm_leaf_summary
from src.processes.extract.interfaces import ExtractTask
from src.runtime import Channels
from src.shared.messages import load_message_texts
from src.shared.prompts import PROMPT_LEAF_SUMMARY
from src.shared.retry import invoke_with_retry
from src.shared.timestamp import get_timestamp
from src.shared.tree_utils import build_sub_area_info

logger = logging.getLogger(__name__)


async def _get_leaf_path(leaf_id: uuid.UUID, root_area_id: uuid.UUID) -> str:
    """Get the full path for a leaf area."""
    leaf_area = await db.LifeAreasManager.get_by_id(leaf_id)
    if not leaf_area:
        return "Unknown"
    descendants = await db.LifeAreasManager.get_descendants(root_area_id)
    for info in build_sub_area_info(descendants, root_area_id):
        if info.area.id == leaf_id:
            return info.path
    return leaf_area.title


async def _extract_and_save_summary(
    task: db.LeafExtractionQueueItem, llm: ChatOpenAI
) -> None:
    """Extract summary from messages and save with embedding."""
    leaf_path = await _get_leaf_path(task.leaf_id, task.root_area_id)
    messages_text = await load_message_texts(task.message_ids)
    if not messages_text:
        logger.warning(
            "No messages for leaf extraction", extra={"leaf_id": str(task.leaf_id)}
        )
        return

    prompt = PROMPT_LEAF_SUMMARY.format(
        leaf_path=leaf_path, messages="\n\n".join(messages_text)
    )
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Extract the summary."},
    ]
    response = await invoke_with_retry(lambda: llm.ainvoke(messages))
    summary = response.content.strip()
    if not summary:
        return

    embeddings = get_embedding_client()
    vector = await embeddings.aembed_query(summary)
    await db.LeafCoverageManager.save_summary(
        task.leaf_id, summary, vector, get_timestamp()
    )
    logger.info(
        "Extracted summary",
        extra={"leaf_id": str(task.leaf_id), "leaf_path": leaf_path},
    )


async def _trigger_knowledge_extraction_if_complete(
    root_area_id: uuid.UUID, channels: Channels
) -> None:
    """Queue knowledge extraction if all leaves are done."""
    coverage_list = await db.LeafCoverageManager.list_by_root_area(root_area_id)
    if not coverage_list or any(
        lc.status in ("pending", "active") for lc in coverage_list
    ):
        return
    root_area = await db.LifeAreasManager.get_by_id(root_area_id)
    if not root_area:
        logger.error("Root area not found", extra={"root_area_id": str(root_area_id)})
        return
    await channels.extract.put(
        ExtractTask(area_id=root_area_id, user_id=root_area.user_id)
    )
    logger.info(
        "Queued knowledge extraction", extra={"root_area_id": str(root_area_id)}
    )


async def _process_task(
    task: db.LeafExtractionQueueItem, llm: ChatOpenAI, channels: Channels
) -> None:
    """Process a single extraction task (already claimed as processing)."""
    extra = {"task_id": str(task.id), "leaf_id": str(task.leaf_id)}
    try:
        await _extract_and_save_summary(task, llm)
        await db.LeafExtractionQueueManager.mark_completed(task.id, get_timestamp())
        logger.info("Completed extraction task", extra=extra)
        await _trigger_knowledge_extraction_if_complete(task.root_area_id, channels)
    except Exception as e:
        logger.exception("Extraction task failed", extra={**extra, "error": str(e)})
        await db.LeafExtractionQueueManager.mark_failed(task.id)


async def _wait_for_tasks_or_shutdown(channels: Channels) -> bool:
    """Wait for poll interval or shutdown. Returns False if shutdown triggered."""
    try:
        await asyncio.wait_for(
            channels.shutdown.wait(), timeout=LEAF_EXTRACT_POLL_INTERVAL
        )
        return False
    except asyncio.TimeoutError:
        return True


async def _process_batch(llm: ChatOpenAI, channels: Channels) -> bool:
    """Process a batch of tasks. Returns False if shutdown triggered."""
    await db.LeafExtractionQueueManager.requeue_failed(LEAF_EXTRACT_MAX_RETRIES)
    tasks = await db.LeafExtractionQueueManager.claim_pending(
        limit=LEAF_EXTRACT_BATCH_SIZE
    )
    if not tasks:
        return await _wait_for_tasks_or_shutdown(channels)
    for task in tasks:
        if channels.shutdown.is_set():
            return False
        await _process_task(task, llm, channels)
    return True


async def _worker_loop(worker_id: int, llm: ChatOpenAI, channels: Channels) -> None:
    """Worker loop that polls the database queue."""
    logger.info("Leaf extract worker %d starting", worker_id)
    while not channels.shutdown.is_set():
        try:
            if not await _process_batch(llm, channels):
                break
        except asyncio.CancelledError:
            logger.info("Leaf extract worker %d cancelled", worker_id)
            raise
        except Exception:
            logger.exception("Leaf extract worker %d error", worker_id)
            await asyncio.sleep(LEAF_EXTRACT_POLL_INTERVAL)
    logger.info("Leaf extract worker %d stopped", worker_id)


async def run_leaf_extract_pool(channels: Channels) -> None:
    """Run the leaf extraction worker pool."""
    llm = get_llm_leaf_summary()
    workers = [
        asyncio.create_task(
            _worker_loop(i, llm, channels), name=f"leaf_extract_worker_{i}"
        )
        for i in range(WORKER_POOL_LEAF_EXTRACT)
    ]
    logger.info(
        "Leaf extract pool started", extra={"worker_count": WORKER_POOL_LEAF_EXTRACT}
    )
    try:
        await channels.shutdown.wait()
    finally:
        for worker in workers:
            worker.cancel()
        await asyncio.gather(*workers, return_exceptions=True)
        logger.info("Leaf extract pool stopped")
