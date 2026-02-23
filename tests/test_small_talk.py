"""Unit tests for small talk response node and routing."""

from unittest.mock import AsyncMock, MagicMock

from langchain_core.messages import AIMessage, HumanMessage
from src.config.settings import HISTORY_LIMIT_EXTRACT_TARGET
from src.domain import ClientMessage, InputMode, User
from src.processes.interview import State, Target
from src.shared.ids import new_id
from src.shared.prompts import PROMPT_SMALL_TALK
from src.workflows.nodes.processing.small_talk_response import small_talk_response
from src.workflows.routers.message_router import route_by_target
from src.workflows.subgraphs.leaf_interview.nodes import completed_area_response
from src.workflows.subgraphs.leaf_interview.routers import route_after_context_load
from src.workflows.subgraphs.leaf_interview.state import LeafInterviewState


def _create_state(
    user: User,
    messages: list,
    target: Target = Target.small_talk,
    area_id=None,
) -> State:
    """Helper to create test State objects."""
    return State(
        user=user,
        message=ClientMessage(data="test"),
        text="test",
        target=target,
        area_id=area_id or new_id(),
        messages=messages,
        messages_to_save={},
        is_fully_covered=False,
    )


def _create_leaf_interview_state(
    user: User,
    messages: list,
    active_leaf_id=None,
    area_id=None,
) -> LeafInterviewState:
    """Helper to create test LeafInterviewState objects."""
    return LeafInterviewState(
        user=user,
        area_id=area_id or new_id(),
        messages=messages,
        messages_to_save={},
        is_fully_covered=False,
        active_leaf_id=active_leaf_id,
    )


class TestSmallTalkResponse:
    """Tests for the small_talk_response node."""

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

    def test_routes_to_leaf_interview(self, sample_user):
        """Should route to leaf_interview for conduct_interview target."""
        state = _create_state(sample_user, [], target=Target.conduct_interview)

        result = route_by_target(state)

        assert result == "leaf_interview"

    def test_routes_to_area_loop(self, sample_user):
        """Should route to area_loop for manage_areas target."""
        state = _create_state(sample_user, [], target=Target.manage_areas)

        result = route_by_target(state)

        assert result == "area_loop"

    def test_routes_to_small_talk_response(self, sample_user):
        """Should route to small_talk_response for small_talk target."""
        state = _create_state(sample_user, [], target=Target.small_talk)

        result = route_by_target(state)

        assert result == "small_talk_response"


class TestRouteAfterContextLoad:
    """Tests for the post-context-load router."""

    def test_routes_to_generate_leaf_response_on_first_turn(self, sample_user):
        """Should route to generate_leaf_response on first turn (no user message)."""
        leaf_id = new_id()
        state = _create_leaf_interview_state(sample_user, [], active_leaf_id=leaf_id)

        result = route_after_context_load(state)

        assert result == "generate_leaf_response"

    def test_routes_to_create_turn_summary_on_subsequent_turn(self, sample_user):
        """Should route to create_turn_summary when user message is present."""
        leaf_id = new_id()
        state = _create_leaf_interview_state(
            sample_user,
            [HumanMessage(content="I have 5 years Python experience")],
            active_leaf_id=leaf_id,
        )

        result = route_after_context_load(state)

        assert result == "create_turn_summary"

    def test_routes_to_completed_area_response_when_all_leaves_done(self, sample_user):
        """Should route to completed_area_response when active_leaf_id is None."""
        state = _create_leaf_interview_state(sample_user, [], active_leaf_id=None)

        result = route_after_context_load(state)

        assert result == "completed_area_response"


class TestCompletedAreaResponse:
    """Tests for the completed_area_response node."""

    async def test_returns_ai_message(self, sample_user):
        """Verify node returns an AI message."""
        area_id = new_id()
        state = _create_leaf_interview_state(
            sample_user,
            [HumanMessage(content="Tell me about my work")],
            area_id=area_id,
        )

        mock_response = MagicMock()
        mock_response.content = "This area has already been documented."

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await completed_area_response(state, mock_llm)

        assert "messages" in result
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert result["messages"][0].content == "This area has already been documented."

    async def test_sets_success_flag(self, sample_user):
        """Verify is_successful is set to True."""
        state = _create_leaf_interview_state(
            sample_user,
            [HumanMessage(content="More about work")],
        )

        mock_response = MagicMock()
        mock_response.content = "Area is complete."

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await completed_area_response(state, mock_llm)

        assert result["is_successful"] is True

    async def test_populates_messages_to_save(self, sample_user):
        """Verify messages_to_save contains the AI response."""
        state = _create_leaf_interview_state(
            sample_user,
            [HumanMessage(content="Hi")],
        )

        mock_response = MagicMock()
        mock_response.content = "Already documented!"

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await completed_area_response(state, mock_llm)

        assert "messages_to_save" in result
        assert len(result["messages_to_save"]) == 1
        bucket = list(result["messages_to_save"].values())[0]
        assert len(bucket) == 1
        assert bucket[0].content == "Already documented!"

    async def test_prompt_includes_area_id(self, sample_user):
        """Verify prompt includes the area ID for reset command."""
        area_id = new_id()
        state = _create_leaf_interview_state(
            sample_user,
            [HumanMessage(content="Work stuff")],
            area_id=area_id,
        )

        mock_response = MagicMock()
        mock_response.content = "Response"

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        await completed_area_response(state, mock_llm)

        mock_llm.ainvoke.assert_called_once()
        call_args = mock_llm.ainvoke.call_args[0][0]
        # First message should contain the area_id in the reset command
        assert str(area_id) in call_args[0].content
