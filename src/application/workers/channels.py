"""Channel definitions for worker communication."""

import asyncio
import uuid
from dataclasses import dataclass, field

from src.domain import ClientMessage


@dataclass
class ExtractTask:
    """Task to extract data from an area for a user."""

    area_id: uuid.UUID
    user_id: uuid.UUID


@dataclass
class Channels:
    """Communication channels between CLI, graph worker, and extract worker."""

    client_message: asyncio.Queue[ClientMessage] = field(default_factory=asyncio.Queue)
    client_response: asyncio.Queue[str] = field(default_factory=asyncio.Queue)
    extract: asyncio.Queue[ExtractTask] = field(default_factory=asyncio.Queue)
