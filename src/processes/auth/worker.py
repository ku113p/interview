"""Auth worker for exchanging external IDs for internal user_ids."""

import asyncio
import logging
import uuid
from functools import partial

from src.config.settings import WORKER_POLL_TIMEOUT
from src.infrastructure.db import managers as db
from src.processes.auth.interfaces import AuthRequest
from src.runtime import Channels, run_worker_pool

logger = logging.getLogger(__name__)

EXTERNAL_ID_NAMESPACE = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")

WORKER_POOL_AUTH = 1


def resolve_user_id(provider: str, external_id: str) -> uuid.UUID:
    """Deterministic mapping from external ID to internal user_id."""
    return uuid.uuid5(EXTERNAL_ID_NAMESPACE, f"{provider}:{external_id}")


async def _process_auth_request(request: AuthRequest) -> None:
    """Process a single auth request."""
    user_id = resolve_user_id(request.provider, request.external_id)

    existing = await db.UsersManager.get_by_id(user_id)
    if not existing:
        name = request.display_name or f"{request.provider}_{request.external_id}"
        await db.UsersManager.create(
            user_id, db.User(id=user_id, name=name, mode="auto")
        )
        logger.info(
            "Created user",
            extra={"user_id": str(user_id), "provider": request.provider},
        )

    request.response_future.set_result(user_id)


async def _auth_worker_loop(worker_id: int, channels: Channels) -> None:
    """Exchange external user ID for internal user_id."""
    while not channels.shutdown.is_set():
        try:
            request = await asyncio.wait_for(
                channels.auth_requests.get(), timeout=WORKER_POLL_TIMEOUT
            )
        except asyncio.TimeoutError:
            continue
        try:
            await _process_auth_request(request)
        except Exception:
            logger.exception("Auth worker %d error", worker_id)
            request.response_future.set_exception(RuntimeError("Auth worker failed"))
        finally:
            channels.auth_requests.task_done()


async def run_auth_pool(channels: Channels) -> None:
    """Run the auth worker pool."""
    worker_fn = partial(_auth_worker_loop, channels=channels)
    await run_worker_pool("auth", worker_fn, WORKER_POOL_AUTH, channels.shutdown)
