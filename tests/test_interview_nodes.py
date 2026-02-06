"""Unit tests for interview analysis and response nodes."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from src.infrastructure.db import repositories as db
from src.shared.ids import new_id
from src.shared.interview_models import CriteriaAnalysis, CriterionCoverage
from src.workflows.nodes.processing.interview_analysis import (
    State as AnalysisState,
)
from src.workflows.nodes.processing.interview_analysis import (
    interview_analysis,
)
from src.workflows.nodes.processing.interview_response import (
    State as ResponseState,
)
from src.workflows.nodes.processing.interview_response import (
    interview_response,
)


class TestInterviewAnalysis:
    """Tests for the interview_analysis node."""

    @pytest.mark.asyncio
    async def test_interview_analysis_saves_message(self, temp_db):
        """Verify user message is saved to the database."""
        # Arrange
        area_id = new_id()
        user_id = new_id()

        # Create required area in DB
        area = db.LifeArea(
            id=area_id,
            title="Test Area",
            parent_id=None,
            user_id=user_id,
        )
        db.LifeAreaManager.create(area_id, area)

        state = AnalysisState(
            area_id=area_id,
            extract_data_tasks=asyncio.Queue(),
            messages=[HumanMessage(content="I have 5 years of Python experience")],
            messages_to_save={},
            was_covered=False,
        )

        mock_analysis = CriteriaAnalysis(
            criteria=[CriterionCoverage(title="Python experience", covered=True)],
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
        saved_messages = db.LifeAreaMessagesManager.list_by_area(area_id)
        assert len(saved_messages) == 1
        assert saved_messages[0].data == "I have 5 years of Python experience"

    @pytest.mark.asyncio
    async def test_interview_analysis_returns_criteria_analysis(self, temp_db):  # noqa: PLR0915
        """Verify structured CriteriaAnalysis is returned."""
        # Arrange
        area_id = new_id()
        user_id = new_id()

        area = db.LifeArea(
            id=area_id,
            title="Test Area",
            parent_id=None,
            user_id=user_id,
        )
        db.LifeAreaManager.create(area_id, area)

        state = AnalysisState(
            area_id=area_id,
            extract_data_tasks=asyncio.Queue(),
            messages=[HumanMessage(content="Test message")],
            messages_to_save={},
            was_covered=False,
        )

        mock_analysis = CriteriaAnalysis(
            criteria=[
                CriterionCoverage(title="Criterion A", covered=True),
                CriterionCoverage(title="Criterion B", covered=False),
            ],
            all_covered=False,
            next_uncovered="Criterion B",
        )

        mock_structured_llm = MagicMock()
        mock_structured_llm.ainvoke = AsyncMock(return_value=mock_analysis)

        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured_llm

        # Act
        result = await interview_analysis(state, mock_llm)

        # Assert
        assert "criteria_analysis" in result
        assert isinstance(result["criteria_analysis"], CriteriaAnalysis)
        assert len(result["criteria_analysis"].criteria) == 2  # noqa: PLR2004
        assert result["criteria_analysis"].next_uncovered == "Criterion B"
        assert result["was_covered"] is False


class TestInterviewResponse:
    """Tests for the interview_response node."""

    @pytest.mark.asyncio
    async def test_interview_response_uses_history(self):
        """Verify conversation history is passed to the LLM."""
        # Arrange
        area_id = new_id()
        history_messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!"),
            HumanMessage(content="Tell me about the role"),
        ]

        analysis = CriteriaAnalysis(
            criteria=[CriterionCoverage(title="Experience", covered=False)],
            all_covered=False,
            next_uncovered="Experience",
        )

        state = ResponseState(
            area_id=area_id,
            extract_data_tasks=asyncio.Queue(),
            messages=history_messages,
            messages_to_save={},
            was_covered=False,
            criteria_analysis=analysis,
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
        assert len(call_args) == 4  # noqa: PLR2004 - 1 system + 3 history messages

    @pytest.mark.asyncio
    async def test_interview_response_requires_analysis(self):
        """Verify null check raises ValueError when criteria_analysis is None."""
        # Arrange
        area_id = new_id()

        state = ResponseState(
            area_id=area_id,
            extract_data_tasks=asyncio.Queue(),
            messages=[HumanMessage(content="Hello")],
            messages_to_save={},
            was_covered=False,
            criteria_analysis=None,  # Explicitly None
        )

        mock_llm = AsyncMock()

        # Act & Assert
        with pytest.raises(ValueError, match="requires criteria_analysis"):
            await interview_response(state, mock_llm)
