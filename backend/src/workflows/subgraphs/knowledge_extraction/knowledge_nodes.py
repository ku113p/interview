"""Knowledge extraction nodes for extract_data workflow."""

import json
import logging
from typing import Literal

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from .state import KnowledgeExtractionState

logger = logging.getLogger(__name__)

_KNOWLEDGE_EXTRACTION_PROMPT = (
    "You are a knowledge extraction agent.\n"
    "Your task is to extract discrete pieces of knowledge about the user "
    "from interview summaries.\n\n"
    "Extract two types of knowledge:\n"
    "1. SKILLS: Abilities, competencies, tools, technologies, languages, "
    "methodologies the user knows or is learning.\n"
    "   Examples: 'Python programming', 'project management', 'Spanish language'\n\n"
    "2. FACTS: Concrete information about the user's life.\n"
    "   Examples: 'Works at Google', 'Has 5 years experience', "
    "'Lives in San Francisco', 'Prefers remote work'\n\n"
    "Rules:\n"
    "- Be specific: 'Python backend development' not just 'programming'\n"
    "- Extract only what is clearly stated or strongly implied\n"
    "- Set confidence based on how explicitly the information was stated:\n"
    "  - 1.0: Directly stated ('I work at Google')\n"
    "  - 0.7-0.9: Strongly implied or mostly clear\n"
    "  - 0.5-0.7: Inferred but less certain\n"
    "- Do not invent or assume information not present in the summary\n"
)


class KnowledgeItem(BaseModel):
    """A single piece of extracted knowledge."""

    content: str = Field(description="The skill or fact description")
    kind: Literal["skill", "fact"] = Field(
        description="Type of knowledge: 'skill' for abilities/competencies, 'fact' for other information"
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence score based on how explicitly stated"
    )


class KnowledgeExtractionResult(BaseModel):
    """Result of knowledge extraction from a summary."""

    items: list[KnowledgeItem] = Field(
        default_factory=list, description="List of extracted knowledge items"
    )


async def extract_knowledge(state: KnowledgeExtractionState, llm: ChatOpenAI) -> dict:
    """Extract skills and facts from the summary content using LLM.

    This node uses structured output to extract:
    - Skills: abilities, competencies, tools, technologies
    - Facts: employment, education, preferences, experiences, relationships
    """
    logger.info(
        "Starting knowledge extraction",
        extra={
            "summary_id": str(state.summary_id),
            "has_content": bool(state.summary_content),
        },
    )

    if not state.summary_content:
        logger.info(
            "Skipping knowledge extraction - no summary content",
            extra={"summary_id": str(state.summary_id)},
        )
        return {"extracted_knowledge": []}

    user_prompt = {"summary": state.summary_content}
    structured_llm = llm.with_structured_output(KnowledgeExtractionResult)

    try:
        result = await structured_llm.ainvoke(
            [
                {"role": "system", "content": _KNOWLEDGE_EXTRACTION_PROMPT},
                {"role": "user", "content": json.dumps(user_prompt)},
            ]
        )
        if not isinstance(result, KnowledgeExtractionResult):
            result = KnowledgeExtractionResult.model_validate(result)

        extracted = [item.model_dump() for item in result.items]
        logger.info(
            "Extracted knowledge items",
            extra={"summary_id": str(state.summary_id), "items_count": len(extracted)},
        )
        return {"extracted_knowledge": extracted}

    except Exception:
        logger.exception(
            "Failed to extract knowledge", extra={"summary_id": str(state.summary_id)}
        )
        return {"extracted_knowledge": []}
