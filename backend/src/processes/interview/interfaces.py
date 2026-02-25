"""Interface types for the interview process."""

import uuid
from dataclasses import dataclass

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
