import os
from dataclasses import dataclass

from langchain_openai import ChatOpenAI


@dataclass
class NewAI:
    model: str
    temperature: int | float | None = None
    base_url: str = "https://openrouter.ai/api/v1"
    api_key: str = os.environ["OPENAI_API_KEY"]

    def build(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=self.model,
            base_url=self.base_url,
            temperature=self.temperature,
            api_key=self.api_key,
        )
