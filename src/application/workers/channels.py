"""Channel types for inter-worker communication."""

import asyncio
import uuid
from dataclasses import dataclass, field

from src.domain import ClientMessage


@dataclass
class ChannelRequest:
    """Envelope for messages from transport to graph workers."""

    correlation_id: uuid.UUID
    user_id: uuid.UUID
    client_message: ClientMessage


@dataclass
class ChannelResponse:
    """Envelope for responses from graph workers to transport."""

    correlation_id: uuid.UUID
    response_text: str


@dataclass
class ExtractTask:
    """Task to extract data from an area for a user."""

    area_id: uuid.UUID
    user_id: uuid.UUID


@dataclass
class AuthRequest:
    """Request to exchange external ID for internal user_id."""

    provider: str
    external_id: str
    display_name: str | None
    response_future: asyncio.Future[uuid.UUID]


@dataclass
class Channels:
    """Shared communication channels between all worker pools."""

    requests: asyncio.Queue[ChannelRequest] = field(default_factory=asyncio.Queue)
    responses: asyncio.Queue[ChannelResponse] = field(default_factory=asyncio.Queue)
    extract: asyncio.Queue[ExtractTask] = field(default_factory=asyncio.Queue)
    auth_requests: asyncio.Queue[AuthRequest] = field(default_factory=asyncio.Queue)
    shutdown: asyncio.Event = field(default_factory=asyncio.Event)
