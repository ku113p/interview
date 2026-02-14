"""Pre-configured LLM instances for workflow nodes.

Uses lazy initialization to avoid API key validation at import time.
"""

from functools import lru_cache

from langchain_openai import ChatOpenAI

from src.config.settings import (
    MAX_TOKENS_CHAT,
    MAX_TOKENS_LEAF_RESPONSE,
    MAX_TOKENS_QUICK_EVALUATE,
    MAX_TOKENS_STRUCTURED,
    MAX_TOKENS_TRANSCRIPTION,
    MODEL_AREA_CHAT,
    MODEL_AUDIO_TRANSCRIPTION,
    MODEL_EXTRACT_TARGET,
    MODEL_LEAF_RESPONSE,
    MODEL_QUICK_EVALUATE,
    MODEL_SMALL_TALK,
    TEMPERATURE_CONVERSATIONAL,
    TEMPERATURE_DETERMINISTIC,
    TEMPERATURE_STRUCTURED,
)
from src.infrastructure.ai import LLMClientBuilder


def _build_llm(
    model: str,
    temperature: float,
    max_tokens: int,
    reasoning: dict | None = None,
) -> ChatOpenAI:
    """Build an LLM with standard configuration."""
    return LLMClientBuilder(
        model,
        temperature=temperature,
        max_tokens=max_tokens,
        reasoning=reasoning,
    ).build()


# Note: reasoning models need minimal reasoning for structured output to avoid
# consuming all tokens on internal reasoning (LengthFinishReasonError)
# Supported values: "low", "medium", "high" (gpt-5.1-codex-mini doesn't support "none")
REASONING_MINIMAL = {"effort": "low"}


# Deterministic LLMs (temperature=0.0)
@lru_cache(maxsize=1)
def get_llm_extract_target() -> ChatOpenAI:
    """Get LLM for target extraction (structured output)."""
    return _build_llm(
        MODEL_EXTRACT_TARGET,
        TEMPERATURE_DETERMINISTIC,
        MAX_TOKENS_STRUCTURED,
        reasoning=REASONING_MINIMAL,
    )


@lru_cache(maxsize=1)
def get_llm_transcribe() -> ChatOpenAI:
    """Get LLM for transcription."""
    return _build_llm(
        MODEL_AUDIO_TRANSCRIPTION, TEMPERATURE_DETERMINISTIC, MAX_TOKENS_TRANSCRIPTION
    )


# Structured output LLMs (temperature=0.2)
@lru_cache(maxsize=1)
def get_llm_area_chat() -> ChatOpenAI:
    """Get LLM for area chat."""
    return _build_llm(MODEL_AREA_CHAT, TEMPERATURE_STRUCTURED, MAX_TOKENS_CHAT)


# Conversational LLMs (temperature=0.5)
@lru_cache(maxsize=1)
def get_llm_small_talk() -> ChatOpenAI:
    """Get LLM for small talk (greetings, app questions)."""
    return _build_llm(MODEL_SMALL_TALK, TEMPERATURE_CONVERSATIONAL, MAX_TOKENS_CHAT)


# Leaf Interview LLMs (new focused flow)
@lru_cache(maxsize=1)
def get_llm_quick_evaluate() -> ChatOpenAI:
    """Get LLM for quick evaluation of user answers (complete/partial/skipped)."""
    return _build_llm(
        MODEL_QUICK_EVALUATE,
        TEMPERATURE_DETERMINISTIC,
        MAX_TOKENS_QUICK_EVALUATE,
        reasoning=REASONING_MINIMAL,
    )


@lru_cache(maxsize=1)
def get_llm_leaf_response() -> ChatOpenAI:
    """Get LLM for generating focused questions about single leaves."""
    return _build_llm(
        MODEL_LEAF_RESPONSE, TEMPERATURE_CONVERSATIONAL, MAX_TOKENS_LEAF_RESPONSE
    )
