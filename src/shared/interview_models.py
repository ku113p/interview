"""Interview-related Pydantic models for structured LLM output."""

from pydantic import BaseModel


class CriterionCoverage(BaseModel):
    """Coverage status for a single criterion."""

    title: str
    covered: bool


class CriteriaAnalysis(BaseModel):
    """Result of analyzing criteria coverage in an interview."""

    criteria: list[CriterionCoverage]
    all_covered: bool
    next_uncovered: str | None  # Which criterion to ask about next
