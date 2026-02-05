import os

API_KEY_ENV = "OPENROUTER_API_KEY"
API_KEY_PREFIX = "sk-or-v1-"
MIN_API_KEY_LENGTH = 20


def load_api_key() -> str:
    api_key = os.environ.get(API_KEY_ENV)
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
    if not api_key.startswith(API_KEY_PREFIX):
        raise ValueError("OPENROUTER_API_KEY has unexpected format")
    if len(api_key) < MIN_API_KEY_LENGTH:
        raise ValueError("OPENROUTER_API_KEY appears too short")
    return api_key
