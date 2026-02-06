import os

# API Configuration
API_KEY_ENV = "OPENROUTER_API_KEY"
API_KEY_PREFIX = "sk-or-v1-"
MIN_API_KEY_LENGTH = 20

# Database Configuration
DB_PATH_ENV = "INTERVIEW_DB_PATH"
DEFAULT_DB_PATH = "interview.db"

# Model Configuration
MODEL_NAME_FLASH = "google/gemini-2.0-flash-001"
MODEL_NAME_INTERVIEW = "deepseek/deepseek-v3.2-speciale"  # Mid-tier reasoning model
MODEL_NAME_AUDIO = "google/gemini-2.0-flash-001"  # Audio transcription model

# Model Assignments (which model to use for each node)
MODEL_EXTRACT_TARGET = MODEL_NAME_FLASH  # Fast classification
MODEL_INTERVIEW = MODEL_NAME_INTERVIEW  # Reasoning-focused conversations
MODEL_AUDIO_TRANSCRIPTION = MODEL_NAME_AUDIO  # Audio processing
MODEL_AREA_CHAT = MODEL_NAME_FLASH  # Area management conversations

# History Limits
HISTORY_LIMIT_GLOBAL = 15  # Default history limit for most nodes
HISTORY_LIMIT_EXTRACT_TARGET = 5  # Limited context for target extraction


def load_api_key() -> str:
    """Load and validate OpenRouter API key from environment.

    Returns:
        str: Valid API key

    Raises:
        RuntimeError: If API key is not set
        ValueError: If API key format is invalid or too short
    """
    api_key = os.environ.get(API_KEY_ENV)
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY not set. Get key at https://openrouter.ai/keys"
        )
    if not api_key.startswith(API_KEY_PREFIX):
        raise ValueError(f"Invalid API key format. Expected: {API_KEY_PREFIX}...")
    if len(api_key) < MIN_API_KEY_LENGTH:
        raise ValueError(
            f"API key too short ({len(api_key)} < {MIN_API_KEY_LENGTH} chars)"
        )
    return api_key


def get_db_path() -> str:
    """Get database path from environment or use default.

    Returns:
        str: Path to SQLite database file
    """
    return os.environ.get(DB_PATH_ENV, DEFAULT_DB_PATH)
