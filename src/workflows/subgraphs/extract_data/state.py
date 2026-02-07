"""State models for extract_data workflow."""

import uuid

from pydantic import BaseModel


class ExtractDataState(BaseModel):
    """State for the extract_data workflow."""

    area_id: uuid.UUID
    area_title: str = ""
    criteria_titles: list[str] = []
    messages: list[str] = []
    extracted_summary: dict[str, str] = {}
    success: bool = False
