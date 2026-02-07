"""Pytest fixtures for testing."""

import os
import tempfile
import uuid
from typing import Generator

import pytest
from src.domain.models import InputMode, User


@pytest.fixture
def sample_user() -> User:
    """Create a sample user for testing."""
    return User(
        id=uuid.UUID("12345678-1234-5678-1234-567812345678"),
        mode=InputMode.auto,
    )


@pytest.fixture
def temp_db() -> Generator[str, None, None]:
    """Create a temporary database for testing.

    Yields:
        str: Path to temporary database file
    """
    # Create a temporary file
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Set the environment variable so get_connection uses this db
    old_db_path = os.environ.get("INTERVIEW_DB_PATH")
    os.environ["INTERVIEW_DB_PATH"] = db_path

    try:
        # Initialize the schema
        from src.infrastructure.db.connection import get_connection

        with get_connection():
            pass  # Schema is auto-initialized

        yield db_path
    finally:
        # Restore original environment
        if old_db_path is not None:
            os.environ["INTERVIEW_DB_PATH"] = old_db_path
        elif "INTERVIEW_DB_PATH" in os.environ:
            del os.environ["INTERVIEW_DB_PATH"]

        # Clean up the temp file
        try:
            os.unlink(db_path)
        except OSError:
            pass


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
