"""Unit tests for load_history module."""

import time
import uuid
from unittest.mock import AsyncMock, patch

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from src.domain.models import InputMode, User
from src.infrastructure.db import managers as db
from src.workflows.nodes.processing.load_history import (
    LoadHistoryState,
    get_formatted_history,
    load_history,
)


class TestGetFormattedHistory:
    """Test the get_formatted_history function."""

    async def test_ai_message_without_tool_calls(self):
        """AI message without tool_calls key should create AIMessage with empty tool_calls.

        This is the main bug fix verification test.
        Current code fails with ValidationError when tool_calls=None.
        Fixed code should pass [] instead.
        """
        # Arrange
        user = User(id=uuid.uuid4(), mode=InputMode.auto)
        mock_history = [
            db.History(
                id=uuid.uuid4(),
                message_data={"role": "ai", "content": "Hello, I'm an AI!"},
                user_id=user.id,
                created_ts=time.time(),
            )
        ]

        with patch.object(
            db.HistoriesManager, "list_by_user", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = mock_history
            # Act
            messages = await get_formatted_history(user)

        # Assert
        assert len(messages) == 1
        assert isinstance(messages[0], AIMessage)
        assert messages[0].content == "Hello, I'm an AI!"
        assert messages[0].tool_calls == []  # Should be empty list, not None

    async def test_ai_message_with_tool_calls(self):
        """AI message with tool_calls should preserve the tool_calls list."""
        # Arrange
        user = User(id=uuid.uuid4(), mode=InputMode.auto)
        tool_calls = [
            {
                "name": "list_life_areas",
                "args": {"user_id": str(user.id)},
                "id": "tool_call_123",
                "type": "tool_call",
            }
        ]
        mock_history = [
            db.History(
                id=uuid.uuid4(),
                message_data={
                    "role": "ai",
                    "content": "",
                    "tool_calls": tool_calls,
                },
                user_id=user.id,
                created_ts=time.time(),
            )
        ]

        with patch.object(
            db.HistoriesManager, "list_by_user", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = mock_history
            # Act
            messages = await get_formatted_history(user)

        # Assert
        assert len(messages) == 1
        assert isinstance(messages[0], AIMessage)
        assert messages[0].content == ""
        assert len(messages[0].tool_calls) == 1
        assert messages[0].tool_calls[0]["name"] == "list_life_areas"

    async def test_ai_message_with_empty_tool_calls(self):
        """AI message with empty tool_calls list should preserve the empty list."""
        # Arrange
        user = User(id=uuid.uuid4(), mode=InputMode.auto)
        mock_history = [
            db.History(
                id=uuid.uuid4(),
                message_data={
                    "role": "ai",
                    "content": "No tools needed",
                    "tool_calls": [],
                },
                user_id=user.id,
                created_ts=time.time(),
            )
        ]

        with patch.object(
            db.HistoriesManager, "list_by_user", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = mock_history
            # Act
            messages = await get_formatted_history(user)

        # Assert
        assert len(messages) == 1
        assert isinstance(messages[0], AIMessage)
        assert messages[0].content == "No tools needed"
        assert messages[0].tool_calls == []

    async def test_human_message(self):
        """User role message should create HumanMessage."""
        # Arrange
        user = User(id=uuid.uuid4(), mode=InputMode.auto)
        mock_history = [
            db.History(
                id=uuid.uuid4(),
                message_data={"role": "user", "content": "Hello, AI!"},
                user_id=user.id,
                created_ts=time.time(),
            )
        ]

        with patch.object(
            db.HistoriesManager, "list_by_user", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = mock_history
            # Act
            messages = await get_formatted_history(user)

        # Assert
        assert len(messages) == 1
        assert isinstance(messages[0], HumanMessage)
        assert messages[0].content == "Hello, AI!"

    async def test_tool_message(self):
        """Tool role message should create ToolMessage with correct attributes."""
        # Arrange
        user = User(id=uuid.uuid4(), mode=InputMode.auto)
        mock_history = [
            db.History(
                id=uuid.uuid4(),
                message_data={
                    "role": "tool",
                    "content": '["result1", "result2"]',
                    "tool_call_id": "tool_123",
                    "name": "search_function",
                },
                user_id=user.id,
                created_ts=time.time(),
            )
        ]

        with patch.object(
            db.HistoriesManager, "list_by_user", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = mock_history
            # Act
            messages = await get_formatted_history(user)

        # Assert
        assert len(messages) == 1
        assert isinstance(messages[0], ToolMessage)
        assert messages[0].content == '["result1", "result2"]'
        assert messages[0].tool_call_id == "tool_123"
        assert messages[0].name == "search_function"

    async def test_tool_message_with_defaults(self):
        """Tool message without optional fields should use default values."""
        # Arrange
        user = User(id=uuid.uuid4(), mode=InputMode.auto)
        mock_history = [
            db.History(
                id=uuid.uuid4(),
                message_data={
                    "role": "tool",
                    "content": "result",
                    # No tool_call_id or name
                },
                user_id=user.id,
                created_ts=time.time(),
            )
        ]

        with patch.object(
            db.HistoriesManager, "list_by_user", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = mock_history
            # Act
            messages = await get_formatted_history(user)

        # Assert
        assert len(messages) == 1
        assert isinstance(messages[0], ToolMessage)
        assert messages[0].content == "result"
        assert messages[0].tool_call_id == "history"
        assert messages[0].name == "history"

    async def test_unsupported_role(self):
        """Unknown role should be skipped with a warning (not raise)."""
        # Arrange
        user = User(id=uuid.uuid4(), mode=InputMode.auto)
        mock_history = [
            db.History(
                id=uuid.uuid4(),
                message_data={"role": "system", "content": "System message"},
                user_id=user.id,
                created_ts=time.time(),
            )
        ]

        with patch.object(
            db.HistoriesManager, "list_by_user", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = mock_history
            # Act - should skip the unknown role and return empty list
            messages = await get_formatted_history(user)

        # Assert - message with unknown role is skipped
        assert messages == []

    async def test_limit_parameter_default(self):
        """Should respect default limit of 15 messages (HISTORY_LIMIT_GLOBAL)."""
        # Arrange
        user = User(id=uuid.uuid4(), mode=InputMode.auto)
        # Create 20 messages
        mock_history = [
            db.History(
                id=uuid.uuid4(),
                message_data={"role": "user", "content": f"Message {i}"},
                user_id=user.id,
                created_ts=time.time() + i,  # Different timestamps
            )
            for i in range(20)
        ]

        with patch.object(
            db.HistoriesManager, "list_by_user", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = mock_history
            # Act
            messages = await get_formatted_history(user)

        # Assert
        assert len(messages) == 15
        # Should get the last 15 messages (5-19)
        assert messages[0].content == "Message 5"
        assert messages[-1].content == "Message 19"

    async def test_limit_parameter_custom(self):
        """Should respect custom limit parameter."""
        # Arrange
        user = User(id=uuid.uuid4(), mode=InputMode.auto)
        mock_history = [
            db.History(
                id=uuid.uuid4(),
                message_data={"role": "user", "content": f"Message {i}"},
                user_id=user.id,
                created_ts=time.time() + i,
            )
            for i in range(10)
        ]

        with patch.object(
            db.HistoriesManager, "list_by_user", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = mock_history
            # Act
            messages = await get_formatted_history(user, limit=3)

        # Assert
        assert len(messages) == 3
        assert messages[0].content == "Message 7"
        assert messages[-1].content == "Message 9"

    async def test_message_ordering(self):
        """Messages should be sorted by created_ts."""
        # Arrange
        user = User(id=uuid.uuid4(), mode=InputMode.auto)
        base_time = time.time()
        # Create messages with out-of-order timestamps
        mock_history = [
            db.History(
                id=uuid.uuid4(),
                message_data={"role": "user", "content": "Third"},
                user_id=user.id,
                created_ts=base_time + 3,
            ),
            db.History(
                id=uuid.uuid4(),
                message_data={"role": "user", "content": "First"},
                user_id=user.id,
                created_ts=base_time + 1,
            ),
            db.History(
                id=uuid.uuid4(),
                message_data={"role": "user", "content": "Second"},
                user_id=user.id,
                created_ts=base_time + 2,
            ),
        ]

        with patch.object(
            db.HistoriesManager, "list_by_user", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = mock_history
            # Act
            messages = await get_formatted_history(user)

        # Assert
        assert len(messages) == 3
        assert messages[0].content == "First"
        assert messages[1].content == "Second"
        assert messages[2].content == "Third"

    async def test_mixed_message_types(self):
        """Should handle a mix of different message types correctly."""
        # Arrange
        user = User(id=uuid.uuid4(), mode=InputMode.auto)
        base_time = time.time()
        mock_history = [
            db.History(
                id=uuid.uuid4(),
                message_data={"role": "user", "content": "Hello"},
                user_id=user.id,
                created_ts=base_time + 1,
            ),
            db.History(
                id=uuid.uuid4(),
                message_data={"role": "ai", "content": "Hi there!"},
                user_id=user.id,
                created_ts=base_time + 2,
            ),
            db.History(
                id=uuid.uuid4(),
                message_data={
                    "role": "ai",
                    "content": "",
                    "tool_calls": [
                        {"name": "test", "args": {}, "id": "1", "type": "tool_call"}
                    ],
                },
                user_id=user.id,
                created_ts=base_time + 3,
            ),
            db.History(
                id=uuid.uuid4(),
                message_data={
                    "role": "tool",
                    "content": "result",
                    "tool_call_id": "1",
                    "name": "test",
                },
                user_id=user.id,
                created_ts=base_time + 4,
            ),
        ]

        with patch.object(
            db.HistoriesManager, "list_by_user", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = mock_history
            # Act
            messages = await get_formatted_history(user)

        # Assert
        assert len(messages) == 4
        assert isinstance(messages[0], HumanMessage)
        assert isinstance(messages[1], AIMessage)
        assert messages[1].tool_calls == []
        assert isinstance(messages[2], AIMessage)
        assert len(messages[2].tool_calls) == 1
        assert isinstance(messages[3], ToolMessage)


class TestLoadHistoryAsync:
    """Test the async load_history function."""

    async def test_load_history_returns_messages(self):
        """load_history should return dict with messages key."""
        # Arrange
        user = User(id=uuid.uuid4(), mode=InputMode.auto)
        state = LoadHistoryState(user=user, messages=[])

        mock_history = [
            db.History(
                id=uuid.uuid4(),
                message_data={"role": "user", "content": "Test message"},
                user_id=user.id,
                created_ts=time.time(),
            )
        ]

        with patch.object(
            db.HistoriesManager, "list_by_user", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = mock_history
            # Act
            result = await load_history(state)

        # Assert
        assert "messages" in result
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], HumanMessage)
        assert result["messages"][0].content == "Test message"

    async def test_load_history_with_empty_history(self):
        """load_history should handle empty history gracefully."""
        # Arrange
        user = User(id=uuid.uuid4(), mode=InputMode.auto)
        state = LoadHistoryState(user=user, messages=[])

        with patch.object(
            db.HistoriesManager, "list_by_user", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = []
            # Act
            result = await load_history(state)

        # Assert
        assert "messages" in result
        assert len(result["messages"]) == 0
