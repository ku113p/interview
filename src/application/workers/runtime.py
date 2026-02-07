"""Runtime that manages worker pools and channels."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from types import TracebackType

from src.application.workers.workers import (
    Channels,
    create_extract_worker,
    create_graph_worker,
)
from src.config.settings import WORKER_POOL_EXTRACT, WORKER_POOL_GRAPH
from src.domain import ClientMessage, User

logger = logging.getLogger(__name__)


async def _run_worker_pool(
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


class Runtime:
    """Manages worker pools and provides message interface for any adapter."""

    def __init__(self, user: User) -> None:
        self._user = user
        self._channels = Channels()
        self._graph_pool: asyncio.Task | None = None
        self._extract_pool: asyncio.Task | None = None

    async def start(self) -> None:
        """Start all worker pools."""
        logger.info("Starting runtime", extra={"user_id": str(self._user.id)})
        self._graph_pool = asyncio.create_task(
            _run_worker_pool(
                "graph",
                create_graph_worker(self._channels, self._user),
                WORKER_POOL_GRAPH,
            )
        )
        self._extract_pool = asyncio.create_task(
            _run_worker_pool(
                "extract",
                create_extract_worker(self._channels),
                WORKER_POOL_EXTRACT,
            )
        )

    async def stop(self) -> None:
        """Stop all worker pools."""
        logger.info("Stopping runtime")
        for pool in (self._graph_pool, self._extract_pool):
            if pool is not None:
                pool.cancel()
                try:
                    await pool
                except asyncio.CancelledError:
                    pass

    async def send(self, message: ClientMessage) -> None:
        """Send a message to be processed by graph workers."""
        await self._channels.client_message.put(message)

    async def receive(self) -> str:
        """Receive a response from graph workers."""
        return await self._channels.client_response.get()

    async def send_and_receive(self, message: ClientMessage) -> str:
        """Send a message and wait for response."""
        await self.send(message)
        return await self.receive()

    async def __aenter__(self) -> "Runtime":
        await self.start()
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        await self.stop()
