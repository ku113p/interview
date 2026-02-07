"""Unit tests for extract_data workflow."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from src.infrastructure.db import repositories as db
from src.workflows.subgraphs.extract_data.nodes import (
    CriterionSummary,
    ExtractionResult,
    extract_summaries,
    load_area_data,
    save_extracted_data,
)
from src.workflows.subgraphs.extract_data.state import ExtractDataState


class TestLoadAreaData:
    """Test the load_area_data function."""

    @pytest.mark.asyncio
    async def test_load_area_data_missing_area(self):
        """Should return success=False when area is not found."""
        # Arrange
        area_id = uuid.uuid4()
        state = ExtractDataState(area_id=area_id)

        with patch.object(db.LifeAreaManager, "get_by_id", return_value=None):
            # Act
            result = await load_area_data(state)

        # Assert
        assert result == {"success": False}

    @pytest.mark.asyncio
    async def test_load_area_data_success(self):
        """Should load area data correctly when area exists."""
        # Arrange
        area_id = uuid.uuid4()
        user_id = uuid.uuid4()
        state = ExtractDataState(area_id=area_id)

        mock_area = db.LifeArea(
            id=area_id,
            title="Career",
            parent_id=None,
            user_id=user_id,
        )
        mock_criteria = [
            db.Criteria(id=uuid.uuid4(), title="Skills", area_id=area_id),
            db.Criteria(id=uuid.uuid4(), title="Goals", area_id=area_id),
        ]
        mock_messages = [
            db.LifeAreaMessage(
                id=uuid.uuid4(),
                data="I want to learn Python",
                area_id=area_id,
                created_ts=1000.0,
            ),
            db.LifeAreaMessage(
                id=uuid.uuid4(),
                data="My goal is to become a senior developer",
                area_id=area_id,
                created_ts=1001.0,
            ),
        ]

        with (
            patch.object(db.LifeAreaManager, "get_by_id", return_value=mock_area),
            patch.object(
                db.CriteriaManager, "list_by_area", return_value=mock_criteria
            ),
            patch.object(
                db.LifeAreaMessagesManager, "list_by_area", return_value=mock_messages
            ),
        ):
            # Act
            result = await load_area_data(state)

        # Assert
        assert result["area_title"] == "Career"
        assert result["criteria_titles"] == ["Skills", "Goals"]
        assert result["messages"] == [
            "I want to learn Python",
            "My goal is to become a senior developer",
        ]

    @pytest.mark.asyncio
    async def test_load_area_data_empty_criteria_and_messages(self):
        """Should handle areas with no criteria or messages."""
        # Arrange
        area_id = uuid.uuid4()
        user_id = uuid.uuid4()
        state = ExtractDataState(area_id=area_id)

        mock_area = db.LifeArea(
            id=area_id,
            title="Empty Area",
            parent_id=None,
            user_id=user_id,
        )

        with (
            patch.object(db.LifeAreaManager, "get_by_id", return_value=mock_area),
            patch.object(db.CriteriaManager, "list_by_area", return_value=[]),
            patch.object(db.LifeAreaMessagesManager, "list_by_area", return_value=[]),
        ):
            # Act
            result = await load_area_data(state)

        # Assert
        assert result["area_title"] == "Empty Area"
        assert result["criteria_titles"] == []
        assert result["messages"] == []


class TestExtractSummaries:
    """Test the extract_summaries function."""

    @pytest.mark.asyncio
    async def test_extract_summaries_empty_criteria(self):
        """Should return success=False when no criteria."""
        # Arrange
        area_id = uuid.uuid4()
        state = ExtractDataState(
            area_id=area_id,
            area_title="Career",
            criteria_titles=[],
            messages=["Some message"],
        )
        mock_llm = AsyncMock()

        # Act
        result = await extract_summaries(state, mock_llm)

        # Assert
        assert result == {"success": False}
        mock_llm.with_structured_output.assert_not_called()

    @pytest.mark.asyncio
    async def test_extract_summaries_empty_messages(self):
        """Should return success=False when no messages."""
        # Arrange
        area_id = uuid.uuid4()
        state = ExtractDataState(
            area_id=area_id,
            area_title="Career",
            criteria_titles=["Skills"],
            messages=[],
        )
        mock_llm = AsyncMock()

        # Act
        result = await extract_summaries(state, mock_llm)

        # Assert
        assert result == {"success": False}
        mock_llm.with_structured_output.assert_not_called()

    @pytest.mark.asyncio
    async def test_extract_summaries_success(self):
        """Should extract summaries successfully."""
        from unittest.mock import MagicMock

        # Arrange
        area_id = uuid.uuid4()
        state = ExtractDataState(
            area_id=area_id,
            area_title="Career",
            criteria_titles=["Skills", "Goals"],
            messages=["I want to learn Python", "My goal is to become senior"],
        )

        mock_result = ExtractionResult(
            summaries=[
                CriterionSummary(criterion="Skills", summary="Wants to learn Python"),
                CriterionSummary(
                    criterion="Goals", summary="Aspires to become senior developer"
                ),
            ]
        )

        mock_structured_llm = AsyncMock()
        mock_structured_llm.ainvoke.return_value = mock_result

        # with_structured_output is a sync method that returns the structured LLM
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured_llm

        # Act
        result = await extract_summaries(state, mock_llm)

        # Assert
        assert result["success"] is True
        assert result["extracted_summary"] == {
            "Skills": "Wants to learn Python",
            "Goals": "Aspires to become senior developer",
        }

    @pytest.mark.asyncio
    async def test_extract_summaries_llm_exception(self):
        """Should return success=False when LLM raises exception."""
        from unittest.mock import MagicMock

        # Arrange
        area_id = uuid.uuid4()
        state = ExtractDataState(
            area_id=area_id,
            area_title="Career",
            criteria_titles=["Skills"],
            messages=["Some message"],
        )

        mock_structured_llm = AsyncMock()
        mock_structured_llm.ainvoke.side_effect = Exception("LLM error")

        # with_structured_output is a sync method that returns the structured LLM
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured_llm

        # Act
        result = await extract_summaries(state, mock_llm)

        # Assert
        assert result == {"success": False}


class TestSaveExtractedData:
    """Test the save_extracted_data function."""

    @pytest.mark.asyncio
    async def test_save_extracted_data_skips_on_failure(self):
        """Should skip saving when success is False."""
        # Arrange
        area_id = uuid.uuid4()
        state = ExtractDataState(
            area_id=area_id,
            success=False,
            extracted_summary={"Skills": "Summary"},
        )

        with patch.object(db.ExtractedDataManager, "create") as mock_create:
            # Act
            result = await save_extracted_data(state)

        # Assert
        assert result == {}
        mock_create.assert_not_called()

    @pytest.mark.asyncio
    async def test_save_extracted_data_skips_on_empty_summary(self):
        """Should skip saving when extracted_summary is empty."""
        # Arrange
        area_id = uuid.uuid4()
        state = ExtractDataState(
            area_id=area_id,
            success=True,
            extracted_summary={},
        )

        with patch.object(db.ExtractedDataManager, "create") as mock_create:
            # Act
            result = await save_extracted_data(state)

        # Assert
        assert result == {}
        mock_create.assert_not_called()

    @pytest.mark.asyncio
    async def test_save_extracted_data_success(self):
        """Should save extracted data to database when successful."""
        # Arrange
        area_id = uuid.uuid4()
        state = ExtractDataState(
            area_id=area_id,
            success=True,
            extracted_summary={"Skills": "Knows Python", "Goals": "Become senior"},
        )

        with patch.object(db.ExtractedDataManager, "create") as mock_create:
            # Act
            result = await save_extracted_data(state)

        # Assert
        assert result == {}
        mock_create.assert_called_once()

        # Verify the data passed to create
        call_args = mock_create.call_args
        data_id = call_args[0][0]
        extracted_data = call_args[0][1]

        assert isinstance(data_id, uuid.UUID)
        assert extracted_data.area_id == area_id
        assert '"Skills": "Knows Python"' in extracted_data.data
        assert '"Goals": "Become senior"' in extracted_data.data
        assert extracted_data.created_ts > 0
