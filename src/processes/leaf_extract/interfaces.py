"""Interface types for the leaf extract process."""

import uuid
from dataclasses import dataclass


@dataclass
class LeafExtractionTask:
    """Task to extract summary from a leaf's interview messages."""

    task_id: uuid.UUID
    leaf_id: uuid.UUID
    root_area_id: uuid.UUID
    message_ids: list[str]
