"""Pre-configured LLM instances for workflow nodes.

Uses lazy initialization to avoid API key validation at import time.
"""

from functools import lru_cache

from langchain_openai import ChatOpenAI

from src.config.settings import (
    MAX_TOKENS_ANALYSIS,
    MAX_TOKENS_CHAT,
    MAX_TOKENS_STRUCTURED,
    MAX_TOKENS_TRANSCRIPTION,
    MODEL_AREA_CHAT,
    MODEL_AUDIO_TRANSCRIPTION,
    MODEL_EXTRACT_TARGET,
    MODEL_INTERVIEW_ANALYSIS,
    MODEL_INTERVIEW_RESPONSE,
    TEMPERATURE_CONVERSATIONAL,
    TEMPERATURE_DETERMINISTIC,
    TEMPERATURE_STRUCTURED,
)
from src.infrastructure.ai import LLMClientBuilder


def _build_llm(model: str, temperature: float, max_tokens: int) -> ChatOpenAI:
    """Build an LLM with standard configuration."""
    return LLMClientBuilder(
        model, temperature=temperature, max_tokens=max_tokens
    ).build()


# Deterministic LLMs (temperature=0.0)
@lru_cache(maxsize=1)
def get_llm_extract_target() -> ChatOpenAI:
    """Get LLM for target extraction."""
    return _build_llm(
        MODEL_EXTRACT_TARGET, TEMPERATURE_DETERMINISTIC, MAX_TOKENS_STRUCTURED
    )


@lru_cache(maxsize=1)
def get_llm_transcribe() -> ChatOpenAI:
    """Get LLM for transcription."""
    return _build_llm(
        MODEL_AUDIO_TRANSCRIPTION, TEMPERATURE_DETERMINISTIC, MAX_TOKENS_TRANSCRIPTION
    )


# Structured output LLMs (temperature=0.2)
@lru_cache(maxsize=1)
def get_llm_interview_analysis() -> ChatOpenAI:
    """Get LLM for interview analysis."""
    return _build_llm(
        MODEL_INTERVIEW_ANALYSIS, TEMPERATURE_STRUCTURED, MAX_TOKENS_ANALYSIS
    )


@lru_cache(maxsize=1)
def get_llm_area_chat() -> ChatOpenAI:
    """Get LLM for area chat."""
    return _build_llm(MODEL_AREA_CHAT, TEMPERATURE_STRUCTURED, MAX_TOKENS_CHAT)


# Conversational LLMs (temperature=0.5)
@lru_cache(maxsize=1)
def get_llm_interview_response() -> ChatOpenAI:
    """Get LLM for interview response."""
    return _build_llm(
        MODEL_INTERVIEW_RESPONSE, TEMPERATURE_CONVERSATIONAL, MAX_TOKENS_CHAT
    )
