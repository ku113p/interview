"""Worker pool utilities for running concurrent workers."""

import asyncio
import logging
from collections.abc import Awaitable, Callable

from src.config.settings import WORKER_SHUTDOWN_CHECK_INTERVAL

logger = logging.getLogger(__name__)


async def run_worker_pool(
    name: str,
    worker_fn: Callable[[int], Awaitable[None]],
    pool_size: int,
    shutdown: asyncio.Event,
) -> None:
    """Run a pool of workers concurrently.

    Args:
        name: Name for logging (e.g., "graph", "extract")
        worker_fn: Async function that takes worker_id and runs until shutdown
        pool_size: Number of workers to spawn
        shutdown: Event that signals all workers to exit
    """
    logger.info("Starting %s worker pool", name, extra={"pool_size": pool_size})

    tasks = [
        asyncio.create_task(worker_fn(worker_id), name=f"{name}-worker-{worker_id}")
        for worker_id in range(pool_size)
    ]

    try:
        # Check shutdown periodically
        while not shutdown.is_set():
            done, pending = await asyncio.wait(
                tasks,
                timeout=WORKER_SHUTDOWN_CHECK_INTERVAL,
                return_when=asyncio.FIRST_COMPLETED,
            )
            if done:
                # A worker exited (crashed or finished)
                break
        # Cancel remaining workers
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    except asyncio.CancelledError:
        logger.info("Shutting down %s worker pool", name)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise
