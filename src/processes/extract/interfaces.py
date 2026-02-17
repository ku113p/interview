"""Interface types for the extract process."""

import uuid
from dataclasses import dataclass


@dataclass
class ExtractTask:
    """Task to extract summary, vector, and knowledge from a completed leaf.

    A leaf IS an area (just one with no children), so we only need area_id.
    User ID and other data are derived from the DB lookup.
    """

    area_id: uuid.UUID


@dataclass
class SummaryVectorizeTask:
    """Task to compute and store the embedding vector for one summary."""

    summary_id: uuid.UUID
