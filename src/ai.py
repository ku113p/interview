import logging
from dataclasses import dataclass

from langchain_openai import ChatOpenAI

from src.config import load_api_key

logger = logging.getLogger(__name__)


@dataclass
class NewAI:
    model: str
    temperature: int | float | None = None
    base_url: str = "https://openrouter.ai/api/v1"
    api_key: str | None = None

    def build(self) -> ChatOpenAI:
        api_key = self.api_key if self.api_key is not None else load_api_key()
        logger.debug("Building AI client", extra={"model": self.model})
        return ChatOpenAI(
            model=self.model,
            base_url=self.base_url,
            temperature=self.temperature,
            api_key=api_key,
        )
