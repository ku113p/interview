"""Pytest fixtures for testing."""

import os
import uuid
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from src.domain.models import InputMode, User


@pytest.fixture(autouse=True)
def _fast_test_timeouts(monkeypatch):
    """Speed up tests by reducing timeout constants.

    Applied automatically to all tests.
    """
    # Fast worker polling for responsive test shutdown
    monkeypatch.setattr("src.config.settings.WORKER_POLL_TIMEOUT", 0.01)
    monkeypatch.setattr("src.config.settings.WORKER_SHUTDOWN_CHECK_INTERVAL", 0.01)

    # Fast retry for testing failure scenarios
    monkeypatch.setattr("src.config.settings.RETRY_INITIAL_WAIT", 0.01)
    monkeypatch.setattr("src.config.settings.RETRY_MAX_WAIT", 0.1)


@pytest.fixture
def sample_user() -> User:
    """Create a sample user for testing."""
    return User(
        id=uuid.UUID("12345678-1234-5678-1234-567812345678"),
        mode=InputMode.auto,
    )


@pytest_asyncio.fixture
async def temp_db(tmp_path: Path) -> AsyncGenerator[str, None]:
    """Isolated test database in a temp directory.

    Uses tmp_path so WAL, SHM, and lock files are all auto-cleaned.
    """
    from src.infrastructure.db.connection import get_connection
    from src.infrastructure.db.schema import _db_initialized_paths

    db_path = str(tmp_path / "test.db")
    old_db_path = os.environ.get("INTERVIEW_DB_PATH")
    os.environ["INTERVIEW_DB_PATH"] = db_path
    try:
        async with get_connection():
            pass  # Schema auto-initialized
        yield db_path
    finally:
        _db_initialized_paths.discard(db_path)
        if old_db_path is not None:
            os.environ["INTERVIEW_DB_PATH"] = old_db_path
        elif "INTERVIEW_DB_PATH" in os.environ:
            del os.environ["INTERVIEW_DB_PATH"]


@pytest.fixture
def mock_history_data() -> list[dict]:
    """Sample history data matching database format.

    Returns:
        List of message dictionaries as stored in database
    """
    return [
        {
            "role": "user",
            "content": "Hello, how are you?",
        },
        {
            "role": "ai",
            "content": "I'm doing well, thank you!",
            # Note: No tool_calls key - this is the bug case
        },
        {
            "role": "ai",
            "content": "",
            "tool_calls": [
                {
                    "name": "list_life_areas",
                    "args": {"user_id": "12345678-1234-5678-1234-567812345678"},
                    "id": "tool_call_123",
                    "type": "tool_call",
                }
            ],
        },
        {
            "role": "tool",
            "content": "[]",
            "tool_call_id": "tool_call_123",
            "name": "list_life_areas",
        },
        {
            "role": "ai",
            "content": "No life areas found.",
            "tool_calls": [],  # Empty list edge case
        },
    ]
