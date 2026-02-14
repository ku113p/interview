"""Interview-related Pydantic models for structured LLM output."""

from typing import Literal

from pydantic import BaseModel, Field


class SubAreaCoverage(BaseModel):
    """Coverage status for a single sub-area."""

    title: str
    covered: bool


class AreaCoverageAnalysis(BaseModel):
    """Result of analyzing sub-area coverage in an interview."""

    sub_areas: list[SubAreaCoverage]
    all_covered: bool
    next_uncovered: str | None  # Which sub-area to ask about next


class LeafEvaluation(BaseModel):
    """Evaluation of user's answer for ONE leaf topic.

    Used by quick_evaluate to determine if the user has fully answered
    a leaf topic, needs more detail, or wants to skip it.
    """

    status: Literal["complete", "partial", "skipped"] = Field(
        description=(
            "complete: user fully answered this topic with enough detail. "
            "partial: user provided some info but we need more detail. "
            "skipped: user explicitly said they don't know or can't answer."
        )
    )
    reason: str = Field(
        description="Brief explanation of why this status was chosen (1-2 sentences)."
    )
