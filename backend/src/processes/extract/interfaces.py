"""Interface types for the extract process."""

import uuid
from dataclasses import dataclass


@dataclass
class ExtractTask:
    """Task to vectorize and extract knowledge from one turn summary."""

    summary_id: uuid.UUID
