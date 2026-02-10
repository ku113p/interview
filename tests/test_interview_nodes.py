"""Unit tests for interview analysis and response nodes."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from src.application.state import State, Target
from src.domain import ClientMessage, InputMode, User
from src.infrastructure.db import managers as db
from src.shared.ids import new_id
from src.shared.interview_models import AreaCoverageAnalysis, SubAreaCoverage
from src.workflows.nodes.processing.interview_analysis import interview_analysis
from src.workflows.nodes.processing.interview_response import interview_response


def _create_state(user: User, area_id, messages, **kwargs) -> State:
    """Helper to create test State objects."""
    return State(
        user=user,
        message=ClientMessage(data="test"),
        text="test",
        target=Target.conduct_interview,
        area_id=area_id,
        messages=messages,
        messages_to_save=kwargs.get("messages_to_save", {}),
        is_fully_covered=kwargs.get("is_fully_covered", False),
        coverage_analysis=kwargs.get("coverage_analysis"),
    )


class TestInterviewAnalysis:
    """Tests for the interview_analysis node."""

    @pytest.mark.asyncio
    async def test_interview_analysis_saves_message(self, temp_db):
        """Verify user message is saved to the database."""
        # Arrange
        area_id = new_id()
        user_id = new_id()
        user = User(id=user_id, mode=InputMode.auto)

        # Create required area in DB
        area = db.LifeArea(
            id=area_id,
            title="Test Area",
            parent_id=None,
            user_id=user_id,
        )
        await db.LifeAreasManager.create(area_id, area)

        state = _create_state(
            user=user,
            area_id=area_id,
            messages=[HumanMessage(content="I have 5 years of Python experience")],
        )

        mock_analysis = AreaCoverageAnalysis(
            sub_areas=[SubAreaCoverage(title="Python experience", covered=True)],
            all_covered=False,
            next_uncovered="JavaScript experience",
        )

        mock_structured_llm = MagicMock()
        mock_structured_llm.ainvoke = AsyncMock(return_value=mock_analysis)

        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured_llm

        # Act
        await interview_analysis(state, mock_llm)

        # Assert - message should be saved to DB
        saved_messages = await db.LifeAreaMessagesManager.list_by_area(area_id)
        assert len(saved_messages) == 1
        assert (
            saved_messages[0].message_text
            == "User: I have 5 years of Python experience"
        )

    @pytest.mark.asyncio
    async def test_interview_analysis_saves_question_and_answer(self, temp_db):
        """Verify AI question and user answer are saved together."""
        # Arrange
        area_id = new_id()
        user_id = new_id()
        user = User(id=user_id, mode=InputMode.auto)

        area = db.LifeArea(
            id=area_id,
            title="Test Area",
            parent_id=None,
            user_id=user_id,
        )
        await db.LifeAreasManager.create(area_id, area)

        state = _create_state(
            user=user,
            area_id=area_id,
            messages=[
                AIMessage(content="What is your Python experience?"),
                HumanMessage(content="I have 5 years"),
            ],
        )

        mock_analysis = AreaCoverageAnalysis(
            sub_areas=[SubAreaCoverage(title="Python experience", covered=True)],
            all_covered=False,
            next_uncovered="JavaScript experience",
        )

        mock_structured_llm = MagicMock()
        mock_structured_llm.ainvoke = AsyncMock(return_value=mock_analysis)

        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured_llm

        # Act
        await interview_analysis(state, mock_llm)

        # Assert - both question and answer should be saved
        saved_messages = await db.LifeAreaMessagesManager.list_by_area(area_id)
        assert len(saved_messages) == 1
        expected = "AI: What is your Python experience?\nUser: I have 5 years"
        assert saved_messages[0].message_text == expected

    @pytest.mark.asyncio
    async def test_interview_analysis_returns_coverage_analysis(self, temp_db):
        """Verify structured AreaCoverageAnalysis is returned."""
        # Arrange
        area_id = new_id()
        user_id = new_id()
        user = User(id=user_id, mode=InputMode.auto)

        area = db.LifeArea(
            id=area_id,
            title="Test Area",
            parent_id=None,
            user_id=user_id,
        )
        await db.LifeAreasManager.create(area_id, area)

        state = _create_state(
            user=user,
            area_id=area_id,
            messages=[HumanMessage(content="Test message")],
        )

        mock_analysis = AreaCoverageAnalysis(
            sub_areas=[
                SubAreaCoverage(title="Sub-area A", covered=True),
                SubAreaCoverage(title="Sub-area B", covered=False),
            ],
            all_covered=False,
            next_uncovered="Sub-area B",
        )

        mock_structured_llm = MagicMock()
        mock_structured_llm.ainvoke = AsyncMock(return_value=mock_analysis)

        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured_llm

        # Act
        result = await interview_analysis(state, mock_llm)

        # Assert
        assert "coverage_analysis" in result
        assert isinstance(result["coverage_analysis"], AreaCoverageAnalysis)
        assert len(result["coverage_analysis"].sub_areas) == 2
        assert result["coverage_analysis"].next_uncovered == "Sub-area B"
        assert result["is_fully_covered"] is False


class TestInterviewResponse:
    """Tests for the interview_response node."""

    @pytest.mark.asyncio
    async def test_interview_response_uses_history(self):
        """Verify conversation history is passed to the LLM."""
        # Arrange
        user = User(id=new_id(), mode=InputMode.auto)
        area_id = new_id()
        history_messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!"),
            HumanMessage(content="Tell me about the role"),
        ]

        analysis = AreaCoverageAnalysis(
            sub_areas=[SubAreaCoverage(title="Experience", covered=False)],
            all_covered=False,
            next_uncovered="Experience",
        )

        state = _create_state(
            user=user,
            area_id=area_id,
            messages=history_messages,
            coverage_analysis=analysis,
        )

        mock_response = MagicMock()
        mock_response.content = "Can you tell me about your experience?"

        mock_llm = AsyncMock(return_value=mock_response)

        # Act
        await interview_response(state, mock_llm)

        # Assert - LLM should be called with history
        mock_llm.ainvoke.assert_called_once()
        call_args = mock_llm.ainvoke.call_args[0][0]
        # First message is system prompt, rest should be history
        assert len(call_args) == 4  # 1 system + 3 history messages

    @pytest.mark.asyncio
    async def test_interview_response_requires_analysis(self):
        """Verify null check raises ValueError when coverage_analysis is None."""
        # Arrange
        user = User(id=new_id(), mode=InputMode.auto)
        area_id = new_id()

        state = _create_state(
            user=user,
            area_id=area_id,
            messages=[HumanMessage(content="Hello")],
            coverage_analysis=None,  # Explicitly None
        )

        mock_llm = AsyncMock()

        # Act & Assert
        with pytest.raises(ValueError, match="requires coverage_analysis"):
            await interview_response(state, mock_llm)
