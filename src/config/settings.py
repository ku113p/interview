import os

# API Configuration
API_KEY_ENV = "OPENROUTER_API_KEY"
API_KEY_PREFIX = "sk-or-v1-"
MIN_API_KEY_LENGTH = 20

# Database Configuration
DB_PATH_ENV = "INTERVIEW_DB_PATH"
DEFAULT_DB_PATH = "interview.db"

# Model Configuration (OpenRouter model identifiers - verified 2026-02)
MODEL_NAME_FLASH_LITE = "google/gemini-2.5-flash-lite"
MODEL_NAME_FLASH = "google/gemini-2.5-flash"
MODEL_NAME_INTERVIEW = "openai/gpt-5.1"
MODEL_NAME_AUDIO = "google/gemini-2.5-flash-lite"

# Model Assignments (which model to use for each node)
MODEL_EXTRACT_TARGET = MODEL_NAME_FLASH_LITE  # Fast classification
MODEL_INTERVIEW = MODEL_NAME_INTERVIEW  # Reasoning-focused conversations
MODEL_AUDIO_TRANSCRIPTION = MODEL_NAME_AUDIO  # Audio processing
MODEL_AREA_CHAT = MODEL_NAME_FLASH  # Area management conversations

# History Limits
HISTORY_LIMIT_GLOBAL = 15  # Default history limit for most nodes
HISTORY_LIMIT_EXTRACT_TARGET = 5  # Limited context for target extraction
HISTORY_LIMIT_INTERVIEW = 8  # History limit for interview response

# Token Limits (max output tokens per node type)
MAX_TOKENS_STRUCTURED = 1024  # For structured output (classification, analysis)
MAX_TOKENS_CHAT = 4096  # For conversational responses
MAX_TOKENS_TRANSCRIPTION = 8192  # For audio transcription

# Model Assignments - Interview Nodes
MODEL_INTERVIEW_ANALYSIS = MODEL_NAME_FLASH  # Fast analysis for criteria coverage
MODEL_INTERVIEW_RESPONSE = MODEL_NAME_INTERVIEW  # Reasoning response generation
MODEL_KNOWLEDGE_EXTRACTION = MODEL_NAME_FLASH  # Knowledge extraction from summaries

# Embedding Configuration
EMBEDDING_MODEL = "openai/text-embedding-3-small"  # Via OpenRouter
EMBEDDING_DIMENSIONS = 1536

# Worker Pool Configuration
WORKER_POOL_GRAPH = 2  # Concurrent graph workers
WORKER_POOL_EXTRACT = 2  # Concurrent extract workers


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
