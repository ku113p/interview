"""Unit tests for message utilities."""

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from src.infrastructure.db import managers as db
from src.shared.ids import new_id
from src.shared.messages import filter_tool_messages, load_message_texts
from src.shared.timestamp import get_timestamp


class TestFilterToolMessages:
    """Test the filter_tool_messages utility."""

    def test_filters_tool_messages(self):
        """Should remove ToolMessage instances."""
        messages = [
            HumanMessage(content="Hello"),
            ToolMessage(content="Tool result", tool_call_id="123"),
            AIMessage(content="Response"),
        ]

        result = filter_tool_messages(messages)

        assert len(result) == 2
        assert all(not isinstance(msg, ToolMessage) for msg in result)

    def test_filters_ai_messages_with_tool_calls(self):
        """Should remove AIMessage instances containing tool_calls."""
        messages = [
            HumanMessage(content="Create an area"),
            AIMessage(
                content="",
                tool_calls=[{"name": "create_life_area", "args": {}, "id": "123"}],
            ),
            ToolMessage(content="Area created", tool_call_id="123"),
            AIMessage(content="I created the area for you"),
        ]

        result = filter_tool_messages(messages)

        assert len(result) == 2
        assert result[0].content == "Create an area"
        assert result[1].content == "I created the area for you"

    def test_preserves_regular_messages(self):
        """Should keep regular human and AI messages."""
        messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!"),
            HumanMessage(content="How are you?"),
            AIMessage(content="I'm doing well"),
        ]

        result = filter_tool_messages(messages)

        assert len(result) == 4
        assert result == messages

    def test_preserves_system_messages(self):
        """Should keep system messages."""
        messages = [
            SystemMessage(content="You are helpful"),
            HumanMessage(content="Hello"),
            AIMessage(content="Hi!"),
        ]

        result = filter_tool_messages(messages)

        assert len(result) == 3
        assert isinstance(result[0], SystemMessage)

    def test_handles_empty_list(self):
        """Should handle empty message list."""
        result = filter_tool_messages([])

        assert result == []

    def test_handles_ai_message_with_empty_tool_calls(self):
        """Should keep AIMessage with empty tool_calls list."""
        messages = [
            AIMessage(content="Regular message", tool_calls=[]),
        ]

        result = filter_tool_messages(messages)

        assert len(result) == 1
        assert result[0].content == "Regular message"

    def test_handles_ai_message_without_tool_calls_attr(self):
        """Should keep AIMessage without tool_calls attribute."""
        messages = [
            AIMessage(content="Regular message"),
        ]

        result = filter_tool_messages(messages)

        assert len(result) == 1
        assert result[0].content == "Regular message"

    def test_filters_mixed_conversation(self):
        """Should correctly filter a realistic conversation with tools."""
        messages = [
            HumanMessage(content="Create area Fitness"),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "create_life_area",
                        "args": {"title": "Fitness"},
                        "id": "call_1",
                    }
                ],
            ),
            ToolMessage(
                content='{"id": "abc", "title": "Fitness"}', tool_call_id="call_1"
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "set_current_area",
                        "args": {"area_id": "abc"},
                        "id": "call_2",
                    }
                ],
            ),
            ToolMessage(content='{"id": "abc"}', tool_call_id="call_2"),
            AIMessage(
                content="I've created the Fitness area. What would you like to discuss?"
            ),
            HumanMessage(content="I exercise 3 times a week"),
            AIMessage(content="That's great! What types of exercise do you do?"),
        ]

        result = filter_tool_messages(messages)

        assert len(result) == 4
        assert result[0].content == "Create area Fitness"
        assert (
            result[1].content
            == "I've created the Fitness area. What would you like to discuss?"
        )
        assert result[2].content == "I exercise 3 times a week"
        assert result[3].content == "That's great! What types of exercise do you do?"


class TestLoadMessageTexts:
    """Tests for the load_message_texts async function."""

    @pytest.mark.asyncio
    async def test_returns_empty_list_for_none(self):
        """Should return empty list when message_ids is None."""
        result = await load_message_texts(None)
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_empty_list_for_empty(self):
        """Should return empty list when message_ids is empty."""
        result = await load_message_texts([])
        assert result == []

    @pytest.mark.asyncio
    async def test_loads_messages_from_db(self, temp_db):
        """Should load message texts from database."""
        area_id = new_id()
        msg1_id, msg2_id = new_id(), new_id()

        # Create test messages
        msg1 = db.LifeAreaMessage(
            id=msg1_id,
            message_text="First message",
            area_id=area_id,
            created_ts=get_timestamp(),
        )
        msg2 = db.LifeAreaMessage(
            id=msg2_id,
            message_text="Second message",
            area_id=area_id,
            created_ts=get_timestamp(),
        )
        await db.LifeAreaMessagesManager.create(msg1_id, msg1)
        await db.LifeAreaMessagesManager.create(msg2_id, msg2)

        result = await load_message_texts([str(msg1_id), str(msg2_id)])

        assert len(result) == 2
        assert result[0] == "First message"
        assert result[1] == "Second message"

    @pytest.mark.asyncio
    async def test_skips_missing_messages(self, temp_db):
        """Should skip messages that don't exist."""
        area_id = new_id()
        existing_id = new_id()
        missing_id = new_id()

        msg = db.LifeAreaMessage(
            id=existing_id,
            message_text="Existing message",
            area_id=area_id,
            created_ts=get_timestamp(),
        )
        await db.LifeAreaMessagesManager.create(existing_id, msg)

        result = await load_message_texts([str(existing_id), str(missing_id)])

        assert len(result) == 1
        assert result[0] == "Existing message"
