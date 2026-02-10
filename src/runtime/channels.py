"""Shared communication channels between all worker pools."""

import asyncio
from dataclasses import dataclass, field

from src.processes.auth.interfaces import AuthRequest
from src.processes.extract.interfaces import ExtractTask
from src.processes.interview.interfaces import ChannelRequest, ChannelResponse


@dataclass
class Channels:
    """Shared communication channels between all worker pools."""

    requests: asyncio.Queue[ChannelRequest] = field(default_factory=asyncio.Queue)
    responses: asyncio.Queue[ChannelResponse] = field(default_factory=asyncio.Queue)
    extract: asyncio.Queue[ExtractTask] = field(default_factory=asyncio.Queue)
    auth_requests: asyncio.Queue[AuthRequest] = field(default_factory=asyncio.Queue)
    shutdown: asyncio.Event = field(default_factory=asyncio.Event)
