import os

# API Configuration
API_KEY_ENV = "OPENROUTER_API_KEY"
API_KEY_PREFIX = "sk-or-v1-"
MIN_API_KEY_LENGTH = 20

# Database Configuration
DB_PATH_ENV = "INTERVIEW_DB_PATH"
DEFAULT_DB_PATH = "interview.db"

# Model Configuration (OpenRouter model identifiers - verified 2026-02)
MODEL_NAME_CODEX_MINI = "openai/gpt-5.1-codex-mini"
MODEL_NAME_FRONTIER = "openai/gpt-5.2"
MODEL_NAME_AUDIO = "google/gemini-2.5-flash-lite"

# Model Assignments (which model to use for each node)
MODEL_EXTRACT_TARGET = MODEL_NAME_CODEX_MINI  # Fast classification
MODEL_INTERVIEW = MODEL_NAME_FRONTIER  # Reasoning-focused conversations
MODEL_AUDIO_TRANSCRIPTION = MODEL_NAME_AUDIO  # Audio processing
MODEL_AREA_CHAT = MODEL_NAME_CODEX_MINI  # Area management conversations
MODEL_SMALL_TALK = MODEL_NAME_CODEX_MINI  # Greetings, app questions

# History Limits
HISTORY_LIMIT_GLOBAL = 15  # Default history limit for most nodes
HISTORY_LIMIT_EXTRACT_TARGET = 5  # Limited context for target extraction
HISTORY_LIMIT_INTERVIEW = 8  # History limit for interview response

# Token Limits (max output tokens per node type)
MAX_TOKENS_STRUCTURED = 1024  # For structured output (classification, analysis)
MAX_TOKENS_CHAT = 4096  # For conversational responses
MAX_TOKENS_TRANSCRIPTION = 8192  # For audio transcription
MAX_TOKENS_KNOWLEDGE = 4096  # For knowledge extraction (needs reasoning tokens)

# Temperature Configuration
TEMPERATURE_DETERMINISTIC = 0.0  # Classification, transcription
TEMPERATURE_STRUCTURED = 0.2  # Analysis, extraction
TEMPERATURE_CONVERSATIONAL = 0.5  # User-facing responses

# Input Token Budgets (for context management)
INPUT_TOKENS_INTERVIEW = 8000  # Interview response context limit

MODEL_KNOWLEDGE_EXTRACTION = (
    MODEL_NAME_CODEX_MINI  # Knowledge extraction from summaries
)

# Model Assignments - Leaf Interview Nodes (new focused flow)
MODEL_QUICK_EVALUATE = MODEL_NAME_CODEX_MINI  # Fast evaluation of user answers
MODEL_LEAF_RESPONSE = MODEL_NAME_CODEX_MINI  # Generate focused questions
MODEL_LEAF_SUMMARY = MODEL_NAME_CODEX_MINI  # Extract summaries from messages

# Token Limits - Leaf Interview
MAX_TURNS_PER_LEAF = 3  # Force-complete a leaf after this many turns
MAX_TOKENS_QUICK_EVALUATE = 1024  # Reasoning model needs headroom beyond output
MAX_TOKENS_LEAF_RESPONSE = 1024  # Short focused questions/responses
MAX_TOKENS_LEAF_SUMMARY = 512  # Brief summary extraction

# Embedding Configuration
EMBEDDING_MODEL = "openai/text-embedding-3-small"  # Via OpenRouter
EMBEDDING_DIMENSIONS = 1536

# Worker Pool Configuration
WORKER_POOL_GRAPH = 2  # Concurrent graph workers
WORKER_POOL_EXTRACT = 2  # Concurrent extract workers
WORKER_POOL_LEAF_EXTRACT = 2  # Concurrent leaf extraction workers

# Leaf Extraction Configuration
LEAF_EXTRACT_POLL_INTERVAL = 1.0  # Seconds between queue polls
LEAF_EXTRACT_MAX_RETRIES = 3  # Max retries for failed extractions
# Batch size balances throughput (fewer DB queries) vs. memory (loading tasks into memory).
# 5 is conservative; can increase for high-throughput scenarios.
LEAF_EXTRACT_BATCH_SIZE = 5


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
