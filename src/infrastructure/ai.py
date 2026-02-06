import logging
from dataclasses import dataclass

from langchain_openai import ChatOpenAI

from src.config.settings import load_api_key

logger = logging.getLogger(__name__)


@dataclass
class NewAI:
    """Wrapper for creating OpenRouter LLM clients with standard configuration."""

    model: str
    temperature: int | float | None = None
    max_tokens: int | None = None
    base_url: str = "https://openrouter.ai/api/v1"
    api_key: str | None = None

    def build(self) -> ChatOpenAI:
        """Build and return a configured ChatOpenAI client.

        Returns:
            ChatOpenAI: Configured LLM client
        """
        api_key = self.api_key if self.api_key is not None else load_api_key()
        logger.debug("Building AI client", extra={"model": self.model})
        return ChatOpenAI(
            model=self.model,
            base_url=self.base_url,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=api_key,
        )
