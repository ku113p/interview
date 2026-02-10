"""Interface types for the auth process."""

import asyncio
import uuid
from dataclasses import dataclass


@dataclass
class AuthRequest:
    """Request to exchange external ID for internal user_id."""

    provider: str
    external_id: str
    display_name: str | None
    response_future: asyncio.Future[uuid.UUID]
