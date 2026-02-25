"""OpenRouter embedding client wrapper."""

from langchain_openai import OpenAIEmbeddings

from src.config.settings import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL, load_api_key


def get_embedding_client() -> OpenAIEmbeddings:
    """Create an OpenAI embeddings client configured for OpenRouter.

    Returns:
        OpenAIEmbeddings instance configured with OpenRouter API.
    """
    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=load_api_key(),
        base_url="https://openrouter.ai/api/v1",
        dimensions=EMBEDDING_DIMENSIONS,
    )
