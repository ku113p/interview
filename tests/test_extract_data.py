"""Unit tests for extract_data workflow."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.infrastructure.db import repositories as db
from src.workflows.subgraphs.extract_data.nodes import (
    CriterionSummary,
    ExtractionResult,
    KnowledgeExtractionResult,
    KnowledgeItem,
    _build_summary_content,
    extract_knowledge,
    extract_summaries,
    load_area_data,
    save_knowledge,
    save_summary,
)
from src.workflows.subgraphs.extract_data.routers import (
    route_extraction_success,
    route_has_data,
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
    async def test_extract_summaries_success(self):
        """Should extract summaries successfully."""
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


class TestRouters:
    """Test the router functions."""

    def test_route_has_data_returns_end_when_no_criteria(self):
        """Should return __end__ when criteria_titles is empty."""
        state = ExtractDataState(
            area_id=uuid.uuid4(),
            criteria_titles=[],
            messages=["Some message"],
        )
        assert route_has_data(state) == "__end__"

    def test_route_has_data_returns_end_when_no_messages(self):
        """Should return __end__ when messages is empty."""
        state = ExtractDataState(
            area_id=uuid.uuid4(),
            criteria_titles=["Skills"],
            messages=[],
        )
        assert route_has_data(state) == "__end__"

    def test_route_has_data_returns_extract_summaries_when_data_exists(self):
        """Should return extract_summaries when both criteria and messages exist."""
        state = ExtractDataState(
            area_id=uuid.uuid4(),
            criteria_titles=["Skills"],
            messages=["Some message"],
        )
        assert route_has_data(state) == "extract_summaries"

    def test_route_extraction_success_returns_end_when_not_successful(self):
        """Should return __end__ when success is False."""
        state = ExtractDataState(
            area_id=uuid.uuid4(),
            success=False,
            extracted_summary={"Skills": "Summary"},
        )
        assert route_extraction_success(state) == "__end__"

    def test_route_extraction_success_returns_end_when_no_summary(self):
        """Should return __end__ when extracted_summary is empty."""
        state = ExtractDataState(
            area_id=uuid.uuid4(),
            success=True,
            extracted_summary={},
        )
        assert route_extraction_success(state) == "__end__"

    def test_route_extraction_success_returns_save_summary_when_successful(self):
        """Should return save_summary when successful with summary."""
        state = ExtractDataState(
            area_id=uuid.uuid4(),
            success=True,
            extracted_summary={"Skills": "Summary"},
        )
        assert route_extraction_success(state) == "save_summary"


class TestBuildSummaryContent:
    """Test the _build_summary_content helper function."""

    def test_builds_content_from_summaries(self):
        """Should combine summaries into content string."""
        extracted = {
            "Skills": "Knows Python and JavaScript",
            "Goals": "Wants to become tech lead",
        }
        result = _build_summary_content(extracted)
        assert "Skills: Knows Python and JavaScript" in result
        assert "Goals: Wants to become tech lead" in result

    def test_excludes_no_response_entries(self):
        """Should exclude 'No response provided' entries."""
        extracted = {
            "Skills": "Knows Python",
            "Goals": "No response provided",
        }
        result = _build_summary_content(extracted)
        assert "Skills: Knows Python" in result
        assert "Goals" not in result

    def test_returns_empty_for_all_no_response(self):
        """Should return empty string when all are no response."""
        extracted = {
            "Skills": "No response provided",
            "Goals": "",
        }
        result = _build_summary_content(extracted)
        assert result == ""


class TestSaveSummary:
    """Test the save_summary function."""

    @pytest.mark.asyncio
    async def test_save_summary_skips_when_no_content(self):
        """Should skip saving when no meaningful content."""
        state = ExtractDataState(
            area_id=uuid.uuid4(),
            success=True,
            extracted_summary={"Skills": "No response provided"},
        )

        with (
            patch("src.infrastructure.embeddings.get_embedding_client") as mock_embed,
            patch.object(db.AreaSummariesManager, "create") as mock_create,
        ):
            result = await save_summary(state)

        assert result == {"summary_content": ""}
        mock_embed.assert_not_called()
        mock_create.assert_not_called()

    @pytest.mark.asyncio
    async def test_save_summary_success(self):
        """Should save summary with embedding."""
        area_id = uuid.uuid4()
        state = ExtractDataState(
            area_id=area_id,
            success=True,
            extracted_summary={"Skills": "Knows Python"},
        )

        mock_embed_client = AsyncMock()
        mock_embed_client.aembed_query.return_value = [0.1, 0.2, 0.3]

        with (
            patch(
                "src.infrastructure.embeddings.get_embedding_client",
                return_value=mock_embed_client,
            ),
            patch.object(db.AreaSummariesManager, "create") as mock_create,
        ):
            result = await save_summary(state)

        assert result["summary_content"] == "Skills: Knows Python"
        mock_embed_client.aembed_query.assert_called_once()
        mock_create.assert_called_once()

        # Verify the data passed to create
        call_args = mock_create.call_args
        summary = call_args[0][1]
        assert summary.area_id == area_id
        assert summary.content == "Skills: Knows Python"
        assert summary.vector == [0.1, 0.2, 0.3]


class TestExtractKnowledge:
    """Test the extract_knowledge function."""

    @pytest.mark.asyncio
    async def test_extract_knowledge_skips_when_no_content(self):
        """Should skip extraction when no summary content."""
        state = ExtractDataState(
            area_id=uuid.uuid4(),
            summary_content="",
        )
        mock_llm = MagicMock()

        result = await extract_knowledge(state, mock_llm)

        assert result == {"extracted_knowledge": []}
        mock_llm.with_structured_output.assert_not_called()

    @pytest.mark.asyncio
    async def test_extract_knowledge_success(self):
        """Should extract knowledge items from summary."""
        state = ExtractDataState(
            area_id=uuid.uuid4(),
            area_title="Career",
            summary_content="Skills: Python programming, JavaScript",
        )

        mock_result = KnowledgeExtractionResult(
            items=[
                KnowledgeItem(
                    content="Python programming", kind="skill", confidence=0.9
                ),
                KnowledgeItem(content="JavaScript", kind="skill", confidence=0.8),
            ]
        )

        mock_structured_llm = AsyncMock()
        mock_structured_llm.ainvoke.return_value = mock_result

        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured_llm

        result = await extract_knowledge(state, mock_llm)

        assert len(result["extracted_knowledge"]) == 2
        assert result["extracted_knowledge"][0]["content"] == "Python programming"
        assert result["extracted_knowledge"][0]["kind"] == "skill"

    @pytest.mark.asyncio
    async def test_extract_knowledge_handles_exception(self):
        """Should return empty list on LLM exception."""
        state = ExtractDataState(
            area_id=uuid.uuid4(),
            summary_content="Some content",
        )

        mock_structured_llm = AsyncMock()
        mock_structured_llm.ainvoke.side_effect = Exception("LLM error")

        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured_llm

        result = await extract_knowledge(state, mock_llm)

        assert result == {"extracted_knowledge": []}

    @pytest.mark.asyncio
    async def test_extract_knowledge_fallback_to_extracted_summary(self):
        """Should compute summary_content from extracted_summary when empty."""
        state = ExtractDataState(
            area_id=uuid.uuid4(),
            area_title="Career",
            summary_content="",  # Empty - fallback should kick in
            extracted_summary={"Skills": "Python programming", "Goals": "Tech lead"},
        )

        mock_result = KnowledgeExtractionResult(
            items=[
                KnowledgeItem(
                    content="Python programming", kind="skill", confidence=0.9
                ),
            ]
        )

        mock_structured_llm = AsyncMock()
        mock_structured_llm.ainvoke.return_value = mock_result

        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured_llm

        result = await extract_knowledge(state, mock_llm)

        # Verify LLM was called (fallback worked)
        mock_structured_llm.ainvoke.assert_called_once()

        # Verify the user prompt contains computed content
        call_args = mock_structured_llm.ainvoke.call_args[0][0]
        user_content = call_args[1]["content"]
        assert "Skills: Python programming" in user_content
        assert "Goals: Tech lead" in user_content

        assert len(result["extracted_knowledge"]) == 1
        assert result["extracted_knowledge"][0]["content"] == "Python programming"


class TestSaveKnowledge:
    """Test the save_knowledge function."""

    @pytest.mark.asyncio
    async def test_save_knowledge_skips_when_no_user_id(self):
        """Should skip saving when no user_id."""
        state = ExtractDataState(
            area_id=uuid.uuid4(),
            user_id=None,
            extracted_knowledge=[
                {"content": "Python", "kind": "skill", "confidence": 0.9}
            ],
        )

        with patch.object(db.UserKnowledgeManager, "create") as mock_create:
            result = await save_knowledge(state)

        assert result == {}
        mock_create.assert_not_called()

    @pytest.mark.asyncio
    async def test_save_knowledge_skips_when_no_knowledge(self):
        """Should skip saving when no extracted knowledge."""
        state = ExtractDataState(
            area_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            extracted_knowledge=[],
        )

        with patch.object(db.UserKnowledgeManager, "create") as mock_create:
            result = await save_knowledge(state)

        assert result == {}
        mock_create.assert_not_called()

    @pytest.mark.asyncio
    async def test_save_knowledge_success(self, temp_db):
        """Should save knowledge items and links."""
        area_id = uuid.uuid4()
        user_id = uuid.uuid4()
        state = ExtractDataState(
            area_id=area_id,
            user_id=user_id,
            extracted_knowledge=[
                {"content": "Python", "kind": "skill", "confidence": 0.9},
                {"content": "Works at Google", "kind": "fact", "confidence": 1.0},
            ],
        )

        # Act
        result = await save_knowledge(state)

        # Assert
        assert result == {}

        # Verify knowledge items were saved
        all_knowledge = db.UserKnowledgeManager.list()
        assert len(all_knowledge) == 2

        python_knowledge = next(k for k in all_knowledge if k.content == "Python")
        assert python_knowledge.kind == "skill"
        assert python_knowledge.confidence == 0.9

        google_knowledge = next(
            k for k in all_knowledge if k.content == "Works at Google"
        )
        assert google_knowledge.kind == "fact"
        assert google_knowledge.confidence == 1.0

        # Verify links were created
        links = db.UserKnowledgeAreasManager.list_by_user(user_id)
        assert len(links) == 2
        assert all(link.user_id == user_id for link in links)
        assert all(link.area_id == area_id for link in links)


def _create_area_with_data(area_id, user_id, criteria_titles, message_texts):
    """Helper to create area with criteria and messages in database."""
    area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
    db.LifeAreaManager.create(area_id, area)

    for title in criteria_titles:
        c = db.Criteria(id=uuid.uuid4(), title=title, area_id=area_id)
        db.CriteriaManager.create(c.id, c)

    for i, text in enumerate(message_texts):
        m = db.LifeAreaMessage(
            id=uuid.uuid4(), data=text, area_id=area_id, created_ts=1000.0 + i
        )
        db.LifeAreaMessagesManager.create(m.id, m)


def _create_mock_llm_for_extraction(summary_result, knowledge_result):
    """Create mock LLM that returns different results for summary vs knowledge."""
    mock_summary_structured = AsyncMock()
    mock_summary_structured.ainvoke.return_value = summary_result

    mock_knowledge_structured = AsyncMock()
    mock_knowledge_structured.ainvoke.return_value = knowledge_result

    def mock_with_structured_output(schema):
        if schema == ExtractionResult:
            return mock_summary_structured
        return mock_knowledge_structured

    mock_llm = MagicMock()
    mock_llm.with_structured_output.side_effect = mock_with_structured_output
    return mock_llm


class TestExtractDataGraphIntegration:
    """Integration tests for the full extract_data graph."""

    @pytest.mark.asyncio
    async def test_full_graph_extracts_and_saves_data(self, temp_db):
        """Test full graph flow from load_area_data to save_knowledge."""
        from src.workflows.subgraphs.extract_data.graph import build_extract_data_graph

        area_id, user_id = uuid.uuid4(), uuid.uuid4()
        _create_area_with_data(
            area_id,
            user_id,
            ["Skills", "Goals"],
            ["I know Python and JavaScript", "My goal is to become a tech lead"],
        )

        summary_result = ExtractionResult(
            summaries=[
                CriterionSummary(
                    criterion="Skills", summary="Proficient in Python and JavaScript"
                ),
                CriterionSummary(
                    criterion="Goals", summary="Aspires to become a tech lead"
                ),
            ]
        )
        knowledge_result = KnowledgeExtractionResult(
            items=[
                KnowledgeItem(
                    content="Python programming", kind="skill", confidence=0.9
                ),
                KnowledgeItem(
                    content="JavaScript programming", kind="skill", confidence=0.9
                ),
                KnowledgeItem(
                    content="Aspires to be tech lead", kind="fact", confidence=0.8
                ),
            ]
        )
        mock_llm = _create_mock_llm_for_extraction(summary_result, knowledge_result)

        mock_embed_client = AsyncMock()
        mock_embed_client.aembed_query.return_value = [0.1, 0.2, 0.3]

        with patch(
            "src.infrastructure.embeddings.get_embedding_client",
            return_value=mock_embed_client,
        ):
            graph = build_extract_data_graph(llm=mock_llm)
            await graph.ainvoke(ExtractDataState(area_id=area_id, user_id=user_id))

        summaries = db.AreaSummariesManager.list_by_area(area_id)
        assert len(summaries) == 1
        assert "Skills: Proficient in Python and JavaScript" in summaries[0].content

        all_knowledge = db.UserKnowledgeManager.list()
        assert len(all_knowledge) == 3

        links = db.UserKnowledgeAreasManager.list_by_user(user_id)
        assert len(links) == 3

    @pytest.mark.asyncio
    async def test_graph_handles_embedding_failure_gracefully(self, temp_db):
        """Test that graph continues when embedding fails."""
        from src.workflows.subgraphs.extract_data.graph import build_extract_data_graph

        area_id, user_id = uuid.uuid4(), uuid.uuid4()
        _create_area_with_data(area_id, user_id, ["Skills"], ["I know Python"])

        summary_result = ExtractionResult(
            summaries=[CriterionSummary(criterion="Skills", summary="Knows Python")]
        )
        mock_structured = AsyncMock()
        mock_structured.ainvoke.return_value = summary_result
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured

        mock_embed_client = AsyncMock()
        mock_embed_client.aembed_query.side_effect = Exception("Embedding service down")

        with patch(
            "src.infrastructure.embeddings.get_embedding_client",
            return_value=mock_embed_client,
        ):
            graph = build_extract_data_graph(llm=mock_llm)
            await graph.ainvoke(ExtractDataState(area_id=area_id, user_id=user_id))

        assert len(db.AreaSummariesManager.list_by_area(area_id)) == 0
        assert len(db.UserKnowledgeManager.list()) == 0

    @pytest.mark.asyncio
    async def test_graph_skips_when_no_data(self, temp_db):
        """Test that graph exits early when area has no criteria or messages."""
        from src.workflows.subgraphs.extract_data.graph import build_extract_data_graph

        area_id, user_id = uuid.uuid4(), uuid.uuid4()
        area = db.LifeArea(id=area_id, title="Empty", parent_id=None, user_id=user_id)
        db.LifeAreaManager.create(area_id, area)

        mock_llm = MagicMock()
        graph = build_extract_data_graph(llm=mock_llm)
        await graph.ainvoke(ExtractDataState(area_id=area_id, user_id=user_id))

        mock_llm.with_structured_output.assert_not_called()
        assert len(db.AreaSummariesManager.list_by_area(area_id)) == 0
        assert len(db.UserKnowledgeManager.list()) == 0
