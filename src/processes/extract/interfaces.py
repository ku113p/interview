"""Interface types for the extract process."""

import uuid
from dataclasses import dataclass


@dataclass
class ExtractTask:
    """Task to extract data from an area for a user."""

    area_id: uuid.UUID
    user_id: uuid.UUID
