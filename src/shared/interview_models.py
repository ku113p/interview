"""Interview-related Pydantic models for structured LLM output."""

from pydantic import BaseModel


class SubAreaCoverage(BaseModel):
    """Coverage status for a single sub-area."""

    title: str
    covered: bool


class AreaCoverageAnalysis(BaseModel):
    """Result of analyzing sub-area coverage in an interview."""

    sub_areas: list[SubAreaCoverage]
    all_covered: bool
    next_uncovered: str | None  # Which sub-area to ask about next
