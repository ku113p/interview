"""Unit tests for small talk response node and routing."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from src.config.settings import HISTORY_LIMIT_EXTRACT_TARGET
from src.domain import ClientMessage, InputMode, User
from src.processes.interview import State, Target
from src.shared.ids import new_id
from src.shared.prompts import PROMPT_SMALL_TALK
from src.workflows.nodes.processing.small_talk_response import small_talk_response
from src.workflows.routers.message_router import route_by_target


def _create_state(
    user: User, messages: list, target: Target = Target.small_talk
) -> State:
    """Helper to create test State objects."""
    return State(
        user=user,
        message=ClientMessage(data="test"),
        text="test",
        target=target,
        area_id=new_id(),
        messages=messages,
        messages_to_save={},
        is_fully_covered=False,
    )


class TestSmallTalkResponse:
    """Tests for the small_talk_response node."""

    @pytest.mark.asyncio
    async def test_returns_ai_message(self):
        """Verify node returns an AI message."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(user, [HumanMessage(content="Hello")])

        mock_response = MagicMock()
        mock_response.content = "Hi! I'm an interview assistant."

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await small_talk_response(state, mock_llm)

        assert "messages" in result
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert result["messages"][0].content == "Hi! I'm an interview assistant."

    @pytest.mark.asyncio
    async def test_sets_success_flag(self):
        """Verify is_successful is set to True."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(user, [HumanMessage(content="What can you do?")])

        mock_response = MagicMock()
        mock_response.content = "I can help you document your life experiences."

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await small_talk_response(state, mock_llm)

        assert result["is_successful"] is True

    @pytest.mark.asyncio
    async def test_populates_messages_to_save(self):
        """Verify messages_to_save contains the AI response."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(user, [HumanMessage(content="Hi")])

        mock_response = MagicMock()
        mock_response.content = "Hello!"

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await small_talk_response(state, mock_llm)

        assert "messages_to_save" in result
        assert len(result["messages_to_save"]) == 1
        # Get the single bucket
        bucket = list(result["messages_to_save"].values())[0]
        assert len(bucket) == 1
        assert bucket[0].content == "Hello!"

    @pytest.mark.asyncio
    async def test_uses_system_prompt(self):
        """Verify LLM is called with the small talk system prompt."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(user, [HumanMessage(content="Hello")])

        mock_response = MagicMock()
        mock_response.content = "Hi there!"

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        await small_talk_response(state, mock_llm)

        mock_llm.ainvoke.assert_called_once()
        call_args = mock_llm.ainvoke.call_args[0][0]
        # First message should be system prompt
        assert call_args[0].content == PROMPT_SMALL_TALK

    @pytest.mark.asyncio
    async def test_limits_history(self):
        """Verify history is limited to HISTORY_LIMIT_EXTRACT_TARGET messages."""
        user = User(id=new_id(), mode=InputMode.auto)
        # Create more messages than the limit
        messages = [
            HumanMessage(content=f"Message {i}")
            for i in range(HISTORY_LIMIT_EXTRACT_TARGET + 5)
        ]
        state = _create_state(user, messages)

        mock_response = MagicMock()
        mock_response.content = "Response"

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        await small_talk_response(state, mock_llm)

        call_args = mock_llm.ainvoke.call_args[0][0]
        # Should be 1 system prompt + limited history
        assert len(call_args) == 1 + HISTORY_LIMIT_EXTRACT_TARGET


class TestRouteByTarget:
    """Tests for the message router."""

    def test_routes_to_interview_analysis(self, sample_user):
        """Should route to interview_analysis for conduct_interview target."""
        state = _create_state(sample_user, [], Target.conduct_interview)

        result = route_by_target(state)

        assert result == "interview_analysis"

    def test_routes_to_area_loop(self, sample_user):
        """Should route to area_loop for manage_areas target."""
        state = _create_state(sample_user, [], Target.manage_areas)

        result = route_by_target(state)

        assert result == "area_loop"

    def test_routes_to_small_talk_response(self, sample_user):
        """Should route to small_talk_response for small_talk target."""
        state = _create_state(sample_user, [], Target.small_talk)

        result = route_by_target(state)

        assert result == "small_talk_response"
