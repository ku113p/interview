"""Interview-related Pydantic models for structured LLM output."""

from typing import Literal

from pydantic import BaseModel, Field


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
