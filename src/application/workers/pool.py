"""Worker pool for concurrent task processing."""

import asyncio
import logging
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)


async def run_worker_pool(
    name: str,
    worker_fn: Callable[[int], Awaitable[None]],
    pool_size: int,
) -> None:
    """Run a pool of workers concurrently.

    Args:
        name: Name for logging (e.g., "graph", "extract")
        worker_fn: Async function that takes worker_id and runs forever
        pool_size: Number of workers to spawn
    """
    logger.info("Starting %s worker pool", name, extra={"pool_size": pool_size})

    tasks = [
        asyncio.create_task(worker_fn(worker_id), name=f"{name}-worker-{worker_id}")
        for worker_id in range(pool_size)
    ]

    try:
        # Wait for all workers (they run forever until cancelled)
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.info("Shutting down %s worker pool", name)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise
