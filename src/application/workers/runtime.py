"""Runtime that manages worker pools and channels."""

import asyncio
import logging
from types import TracebackType

from src.application.workers.channels import Channels
from src.application.workers.extract_worker import create_extract_worker
from src.application.workers.graph_worker import create_graph_worker
from src.application.workers.pool import run_worker_pool
from src.config.settings import WORKER_POOL_EXTRACT, WORKER_POOL_GRAPH
from src.domain import ClientMessage, User

logger = logging.getLogger(__name__)


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
            run_worker_pool(
                "graph",
                create_graph_worker(self._channels, self._user),
                WORKER_POOL_GRAPH,
            )
        )
        self._extract_pool = asyncio.create_task(
            run_worker_pool(
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
