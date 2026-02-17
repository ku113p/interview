"""Unit tests for knowledge_extraction workflow."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.infrastructure.db import managers as db
from src.shared.ids import new_id
from src.shared.timestamp import get_timestamp
from src.workflows.subgraphs.knowledge_extraction.nodes import (
    ExtractionResult,
    KnowledgeExtractionResult,
    KnowledgeItem,
    SubAreaSummary,
    _build_summary_content,
    extract_knowledge,
    extract_summaries,
    load_area_data,
    persist_extraction,
    prepare_summary,
)
from src.workflows.subgraphs.knowledge_extraction.routers import (
    route_extraction_success,
    route_has_data,
)
from src.workflows.subgraphs.knowledge_extraction.state import KnowledgeExtractionState


class TestLoadAreaData:
    """Test the load_area_data function."""

    @pytest.mark.asyncio
    async def test_load_area_data_missing_area(self):
        """Should return is_successful=False when area is not found."""
        area_id = uuid.uuid4()
        state = KnowledgeExtractionState(area_id=area_id)

        with patch.object(
            db.LifeAreasManager, "get_by_id", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = None
            result = await load_area_data(state)

        assert result == {"is_successful": False}

    @pytest.mark.asyncio
    async def test_load_area_data_no_leaf_summaries(self):
        """Should return is_successful=False when no leaf summaries available."""
        area_id = uuid.uuid4()
        user_id = uuid.uuid4()
        leaf_id = uuid.uuid4()
        state = KnowledgeExtractionState(area_id=area_id)

        mock_area = db.LifeArea(
            id=area_id, title="Career", parent_id=None, user_id=user_id
        )
        mock_sub_area = db.LifeArea(
            id=leaf_id, title="Skills", parent_id=area_id, user_id=user_id
        )

        with (
            patch.object(
                db.LifeAreasManager, "get_by_id", new_callable=AsyncMock
            ) as mock_get,
            patch.object(
                db.LifeAreasManager, "get_descendants", new_callable=AsyncMock
            ) as mock_get_descendants,
            patch.object(
                db.SummariesManager, "list_by_area", new_callable=AsyncMock
            ) as mock_list_summaries,
        ):
            mock_get.return_value = mock_area
            mock_get_descendants.return_value = [mock_sub_area]
            mock_list_summaries.return_value = []  # No summaries
            result = await load_area_data(state)

        assert result["is_successful"] is False
        assert result["area_title"] == "Career"

    @pytest.mark.asyncio
    async def test_load_area_data_leaf_with_summary(self):
        """Should load summary from summaries table for leaf area (no sub-areas)."""
        area_id = uuid.uuid4()
        user_id = uuid.uuid4()
        state = KnowledgeExtractionState(area_id=area_id)

        mock_area = db.LifeArea(
            id=area_id, title="Leaf Area", parent_id=None, user_id=user_id
        )
        mock_summary = db.Summary(
            id=new_id(),
            area_id=area_id,
            summary_text="I'm a software engineer.",
            created_at=1000.0,
        )

        with (
            patch.object(
                db.LifeAreasManager, "get_by_id", new_callable=AsyncMock
            ) as mock_get,
            patch.object(
                db.LifeAreasManager, "get_descendants", new_callable=AsyncMock
            ) as mock_get_descendants,
            patch.object(
                db.SummariesManager, "list_by_area", new_callable=AsyncMock
            ) as mock_list_summaries,
        ):
            mock_get.return_value = mock_area
            mock_get_descendants.return_value = []
            mock_list_summaries.return_value = [mock_summary]
            result = await load_area_data(state)

        assert result["area_title"] == "Leaf Area"
        assert result["sub_areas_tree"] == "Leaf Area"
        assert result["sub_area_paths"] == ["Leaf Area"]
        assert result["use_leaf_summaries"] is True
        assert result["is_leaf"] is True
        assert result["user_id"] == user_id
        assert result["messages"] == []
        assert result["extracted_summary"] == {"Leaf Area": "I'm a software engineer."}

    @pytest.mark.asyncio
    async def test_load_area_data_leaf_without_summary(self):
        """Should return is_successful=False for leaf area without summaries."""
        area_id = uuid.uuid4()
        user_id = uuid.uuid4()
        state = KnowledgeExtractionState(area_id=area_id)

        mock_area = db.LifeArea(
            id=area_id, title="Empty Leaf", parent_id=None, user_id=user_id
        )

        with (
            patch.object(
                db.LifeAreasManager, "get_by_id", new_callable=AsyncMock
            ) as mock_get,
            patch.object(
                db.LifeAreasManager, "get_descendants", new_callable=AsyncMock
            ) as mock_get_descendants,
            patch.object(
                db.SummariesManager, "list_by_area", new_callable=AsyncMock
            ) as mock_list_summaries,
        ):
            mock_get.return_value = mock_area
            mock_get_descendants.return_value = []
            mock_list_summaries.return_value = []
            result = await load_area_data(state)

        assert result["is_successful"] is False

    @pytest.mark.asyncio
    async def test_load_area_data_uses_leaf_summaries(self):
        """Should use pre-extracted leaf summaries when available."""
        area_id = uuid.uuid4()
        user_id = uuid.uuid4()
        leaf_id = uuid.uuid4()
        state = KnowledgeExtractionState(area_id=area_id)

        mock_area = db.LifeArea(
            id=area_id, title="Career", parent_id=None, user_id=user_id
        )
        mock_sub_area = db.LifeArea(
            id=leaf_id, title="Skills", parent_id=area_id, user_id=user_id
        )
        mock_summary = db.Summary(
            id=new_id(),
            area_id=leaf_id,
            summary_text="Has Python experience",
            created_at=1000.0,
        )

        with (
            patch.object(
                db.LifeAreasManager, "get_by_id", new_callable=AsyncMock
            ) as mock_get,
            patch.object(
                db.LifeAreasManager, "get_descendants", new_callable=AsyncMock
            ) as mock_get_descendants,
            patch.object(
                db.SummariesManager, "list_by_area", new_callable=AsyncMock
            ) as mock_list_summaries,
        ):
            mock_get.return_value = mock_area
            mock_get_descendants.return_value = [mock_sub_area]
            mock_list_summaries.return_value = [mock_summary]
            result = await load_area_data(state)

        assert result["area_title"] == "Career"
        assert result["use_leaf_summaries"] is True
        assert result["extracted_summary"] == {"Skills": "Has Python experience"}
        assert result["messages"] == []


class TestExtractSummaries:
    """Test the extract_summaries function."""

    @pytest.mark.asyncio
    async def test_extract_summaries_success(self):
        """Should extract summaries successfully."""
        area_id = uuid.uuid4()
        state = KnowledgeExtractionState(
            area_id=area_id,
            area_title="Career",
            sub_areas_tree="Goals\nSkills",
            sub_area_paths=["Skills", "Goals"],
            messages=["I want to learn Python", "My goal is to become senior"],
        )

        mock_result = ExtractionResult(
            summaries=[
                SubAreaSummary(sub_area="Skills", summary="Wants to learn Python"),
                SubAreaSummary(
                    sub_area="Goals", summary="Aspires to become senior developer"
                ),
            ]
        )

        mock_structured_llm = AsyncMock()
        mock_structured_llm.ainvoke.return_value = mock_result

        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured_llm

        result = await extract_summaries(state, mock_llm)

        assert result["is_successful"] is True
        assert result["extracted_summary"] == {
            "Skills": "Wants to learn Python",
            "Goals": "Aspires to become senior developer",
        }

    @pytest.mark.asyncio
    async def test_extract_summaries_llm_exception(self):
        """Should return is_successful=False when LLM raises exception."""
        area_id = uuid.uuid4()
        state = KnowledgeExtractionState(
            area_id=area_id,
            area_title="Career",
            sub_areas_tree="Skills",
            sub_area_paths=["Skills"],
            messages=["Some message"],
        )

        mock_structured_llm = AsyncMock()
        mock_structured_llm.ainvoke.side_effect = Exception("LLM error")

        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured_llm

        result = await extract_summaries(state, mock_llm)

        assert result == {"is_successful": False}

    @pytest.mark.asyncio
    async def test_extract_summaries_skips_when_using_leaf_summaries(self):
        """Should skip LLM call when using pre-extracted leaf summaries."""
        area_id = uuid.uuid4()
        state = KnowledgeExtractionState(
            area_id=area_id,
            area_title="Career",
            use_leaf_summaries=True,
            extracted_summary={"Skills": "Has Python experience"},
        )

        mock_llm = MagicMock()

        result = await extract_summaries(state, mock_llm)

        assert result["is_successful"] is True
        mock_llm.with_structured_output.assert_not_called()


class TestRouters:
    """Test the router functions."""

    def test_route_has_data_returns_end_when_no_sub_areas(self):
        """Should return __end__ when sub_area_paths is empty."""
        state = KnowledgeExtractionState(
            area_id=uuid.uuid4(),
            sub_area_paths=[],
            messages=["Some message"],
        )
        assert route_has_data(state) == "__end__"

    def test_route_has_data_returns_end_when_no_messages(self):
        """Should return __end__ when messages is empty."""
        state = KnowledgeExtractionState(
            area_id=uuid.uuid4(),
            sub_area_paths=["Skills"],
            messages=[],
        )
        assert route_has_data(state) == "__end__"

    def test_route_has_data_returns_extract_summaries_when_data_exists(self):
        """Should return extract_summaries when both sub-areas and messages exist."""
        state = KnowledgeExtractionState(
            area_id=uuid.uuid4(),
            sub_area_paths=["Skills"],
            messages=["Some message"],
        )
        assert route_has_data(state) == "extract_summaries"

    def test_route_has_data_returns_extract_summaries_when_leaf_summaries(self):
        """Should return extract_summaries when using pre-extracted leaf summaries."""
        state = KnowledgeExtractionState(
            area_id=uuid.uuid4(),
            sub_area_paths=["Skills"],
            messages=[],  # Empty messages
            use_leaf_summaries=True,
            extracted_summary={"Skills": "Has Python experience"},
        )
        assert route_has_data(state) == "extract_summaries"

    def test_route_extraction_success_returns_end_when_not_successful(self):
        """Should return __end__ when is_successful is False."""
        state = KnowledgeExtractionState(
            area_id=uuid.uuid4(),
            is_successful=False,
            extracted_summary={"Skills": "Summary"},
        )
        assert route_extraction_success(state) == "__end__"

    def test_route_extraction_success_returns_end_when_no_summary(self):
        """Should return __end__ when extracted_summary is empty."""
        state = KnowledgeExtractionState(
            area_id=uuid.uuid4(),
            is_successful=True,
            extracted_summary={},
        )
        assert route_extraction_success(state) == "__end__"

    def test_route_extraction_success_returns_prepare_summary(self):
        """Should return prepare_summary when successful with summary."""
        state = KnowledgeExtractionState(
            area_id=uuid.uuid4(),
            is_successful=True,
            extracted_summary={"Skills": "Summary"},
        )
        assert route_extraction_success(state) == "prepare_summary"


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


class TestPrepareSummary:
    """Test the prepare_summary function."""

    @pytest.mark.asyncio
    async def test_prepare_summary_skips_when_no_content(self):
        """Should skip when no meaningful content."""
        state = KnowledgeExtractionState(
            area_id=uuid.uuid4(),
            is_successful=True,
            extracted_summary={"Skills": "No response provided"},
        )

        with patch("src.infrastructure.embeddings.get_embedding_client") as mock_embed:
            result = await prepare_summary(state)

        assert result == {"summary_content": ""}
        mock_embed.assert_not_called()

    @pytest.mark.asyncio
    async def test_prepare_summary_returns_vector(self):
        """Should return summary content and vector in state (no DB write)."""
        area_id = uuid.uuid4()
        state = KnowledgeExtractionState(
            area_id=area_id,
            is_successful=True,
            is_leaf=True,
            extracted_summary={"Skills": "Knows Python"},
        )

        mock_embed_client = AsyncMock()
        mock_embed_client.aembed_query.return_value = [0.1, 0.2, 0.3]

        with patch(
            "src.infrastructure.embeddings.get_embedding_client",
            return_value=mock_embed_client,
        ):
            result = await prepare_summary(state)

        assert result["summary_content"] == "Skills: Knows Python"
        assert result["summary_vector"] == [0.1, 0.2, 0.3]
        mock_embed_client.aembed_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_prepare_summary_handles_embedding_failure(self):
        """Should return summary content without vector when embedding fails."""
        state = KnowledgeExtractionState(
            area_id=uuid.uuid4(),
            is_successful=True,
            is_leaf=True,
            extracted_summary={"Skills": "Knows Python"},
        )

        mock_embed_client = AsyncMock()
        mock_embed_client.aembed_query.side_effect = Exception("Embedding error")

        with patch(
            "src.infrastructure.embeddings.get_embedding_client",
            return_value=mock_embed_client,
        ):
            result = await prepare_summary(state)

        assert result == {"summary_content": "Skills: Knows Python"}

    @pytest.mark.asyncio
    async def test_prepare_summary_skips_embedding_for_root_area(self):
        """Should skip embedding and return content for root areas (is_leaf=False)."""
        state = KnowledgeExtractionState(
            area_id=uuid.uuid4(),
            is_successful=True,
            is_leaf=False,
            extracted_summary={"Skills": "Knows Python"},
        )

        with patch("src.infrastructure.embeddings.get_embedding_client") as mock_embed:
            result = await prepare_summary(state)

        assert result == {"summary_content": "Skills: Knows Python"}
        mock_embed.assert_not_called()


class TestExtractKnowledge:
    """Test the extract_knowledge function."""

    @pytest.mark.asyncio
    async def test_extract_knowledge_skips_when_no_content(self):
        """Should skip extraction when no summary content."""
        state = KnowledgeExtractionState(
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
        state = KnowledgeExtractionState(
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
        state = KnowledgeExtractionState(
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
        state = KnowledgeExtractionState(
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

        mock_structured_llm.ainvoke.assert_called_once()

        call_args = mock_structured_llm.ainvoke.call_args[0][0]
        user_content = call_args[1]["content"]
        assert "Skills: Python programming" in user_content
        assert "Goals: Tech lead" in user_content

        assert len(result["extracted_knowledge"]) == 1
        assert result["extracted_knowledge"][0]["content"] == "Python programming"


class TestPersistExtraction:
    """Test the persist_extraction function."""

    @pytest.mark.asyncio
    async def test_persist_extraction_atomic_write(self, temp_db):
        """Should write knowledge items and mark_extracted atomically."""
        area_id = uuid.uuid4()
        user_id = uuid.uuid4()

        area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)

        state = KnowledgeExtractionState(
            area_id=area_id,
            user_id=user_id,
            area_title="Career",
            extracted_knowledge=[
                {"content": "Python", "kind": "skill", "confidence": 0.9},
                {"content": "Works at Google", "kind": "fact", "confidence": 1.0},
            ],
        )

        result = await persist_extraction(state)
        assert result == {}

        all_knowledge = await db.UserKnowledgeManager.list()
        assert len(all_knowledge) == 2

        links = await db.UserKnowledgeAreasManager.list_by_user(user_id)
        assert len(links) == 2

        updated_area = await db.LifeAreasManager.get_by_id(area_id)
        assert updated_area.extracted_at is not None

    @pytest.mark.asyncio
    async def test_persist_extraction_skips_knowledge_when_no_user(self, temp_db):
        """Should skip knowledge save when no user_id."""
        area_id = uuid.uuid4()

        area = db.LifeArea(
            id=area_id, title="Career", parent_id=None, user_id=uuid.uuid4()
        )
        await db.LifeAreasManager.create(area_id, area)

        state = KnowledgeExtractionState(
            area_id=area_id,
            user_id=None,
            extracted_knowledge=[
                {"content": "Python", "kind": "skill", "confidence": 0.9},
            ],
        )

        await persist_extraction(state)

        all_knowledge = await db.UserKnowledgeManager.list()
        assert len(all_knowledge) == 0

        updated_area = await db.LifeAreasManager.get_by_id(area_id)
        assert updated_area.extracted_at is not None

    @pytest.mark.asyncio
    async def test_persist_extraction_rolls_back_on_failure(self, temp_db):
        """Should roll back all writes if mark_extracted fails."""
        area_id = uuid.uuid4()
        user_id = uuid.uuid4()

        area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)

        state = KnowledgeExtractionState(
            area_id=area_id,
            user_id=user_id,
            area_title="Career",
            extracted_knowledge=[
                {"content": "Python", "kind": "skill", "confidence": 0.9},
            ],
        )

        with patch.object(
            db.LifeAreasManager,
            "mark_extracted",
            side_effect=RuntimeError("simulated failure"),
        ):
            with pytest.raises(RuntimeError, match="simulated failure"):
                await persist_extraction(state)

        all_knowledge = await db.UserKnowledgeManager.list()
        assert len(all_knowledge) == 0

        updated_area = await db.LifeAreasManager.get_by_id(area_id)
        assert updated_area.extracted_at is None


async def _create_area_with_leaf_summaries(area_id, user_id, sub_area_summaries):
    """Helper to create area with sub-areas and per-turn summaries in database.

    Args:
        area_id: Root area UUID
        user_id: User UUID
        sub_area_summaries: Dict of {title: summary_text} for each sub-area
    """
    now = get_timestamp()
    area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
    await db.LifeAreasManager.create(area_id, area)

    for title, summary in sub_area_summaries.items():
        sub_area_id = uuid.uuid4()
        sub_area = db.LifeArea(
            id=sub_area_id,
            title=title,
            parent_id=area_id,
            user_id=user_id,
            covered_at=now,
        )
        await db.LifeAreasManager.create(sub_area_id, sub_area)

        await db.SummariesManager.create_summary(
            area_id=sub_area_id,
            summary_text=summary,
            created_at=now,
        )


def _create_knowledge_mock_llm():
    """Create mock LLM returning sample knowledge items."""
    knowledge_result = KnowledgeExtractionResult(
        items=[
            KnowledgeItem(content="Python programming", kind="skill", confidence=0.9),
            KnowledgeItem(
                content="JavaScript programming", kind="skill", confidence=0.9
            ),
            KnowledgeItem(
                content="Aspires to be tech lead", kind="fact", confidence=0.8
            ),
        ]
    )
    mock_structured = AsyncMock()
    mock_structured.ainvoke.return_value = knowledge_result
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured
    return mock_llm


async def _verify_full_graph_results(area_id, user_id):
    """Verify graph created knowledge, links, and marked area extracted."""
    all_knowledge = await db.UserKnowledgeManager.list()
    assert len(all_knowledge) == 3

    links = await db.UserKnowledgeAreasManager.list_by_user(user_id)
    assert len(links) == 3

    area = await db.LifeAreasManager.get_by_id(area_id)
    assert area.extracted_at is not None


class TestKnowledgeExtractionGraphIntegration:
    """Integration tests for the full knowledge_extraction graph."""

    @pytest.mark.asyncio
    async def test_full_graph_extracts_and_saves_data(self, temp_db):
        """Test full graph flow from load_area_data to persist_extraction."""
        from src.workflows.subgraphs.knowledge_extraction.graph import (
            build_knowledge_extraction_graph,
        )

        area_id, user_id = uuid.uuid4(), uuid.uuid4()
        await _create_area_with_leaf_summaries(
            area_id,
            user_id,
            {"Skills": "Proficient in Python and JavaScript", "Goals": "Tech lead"},
        )

        # Root area (has descendants) — embedding is skipped, no mock needed
        graph = build_knowledge_extraction_graph(llm=_create_knowledge_mock_llm())
        await graph.ainvoke(KnowledgeExtractionState(area_id=area_id, user_id=user_id))

        await _verify_full_graph_results(area_id, user_id)

    @pytest.mark.asyncio
    async def test_graph_handles_embedding_failure_gracefully(self, temp_db):
        """Test that graph continues when embedding fails — no knowledge saved."""
        from src.workflows.subgraphs.knowledge_extraction.graph import (
            build_knowledge_extraction_graph,
        )

        area_id, user_id = uuid.uuid4(), uuid.uuid4()
        now = get_timestamp()

        # Create a leaf area (no descendants) so is_leaf=True and embedding is attempted
        area = db.LifeArea(
            id=area_id, title="Skills", parent_id=None, user_id=user_id, covered_at=now
        )
        await db.LifeAreasManager.create(area_id, area)
        await db.SummariesManager.create_summary(
            area_id=area_id, summary_text="Knows Python", created_at=now
        )

        mock_structured = AsyncMock()
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured

        mock_embed_client = AsyncMock()
        mock_embed_client.aembed_query.side_effect = Exception("Embedding service down")

        with patch(
            "src.infrastructure.embeddings.get_embedding_client",
            return_value=mock_embed_client,
        ):
            graph = build_knowledge_extraction_graph(llm=mock_llm)
            await graph.ainvoke(
                KnowledgeExtractionState(area_id=area_id, user_id=user_id)
            )

        all_knowledge = await db.UserKnowledgeManager.list()
        assert len(all_knowledge) == 0

    @pytest.mark.asyncio
    async def test_graph_skips_when_no_data(self, temp_db):
        """Test that graph exits early when area has no sub-areas or summaries."""
        from src.workflows.subgraphs.knowledge_extraction.graph import (
            build_knowledge_extraction_graph,
        )

        area_id, user_id = uuid.uuid4(), uuid.uuid4()
        area = db.LifeArea(id=area_id, title="Empty", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)

        mock_llm = MagicMock()
        graph = build_knowledge_extraction_graph(llm=mock_llm)
        await graph.ainvoke(KnowledgeExtractionState(area_id=area_id, user_id=user_id))

        mock_llm.with_structured_output.assert_not_called()
        all_knowledge = await db.UserKnowledgeManager.list()
        assert len(all_knowledge) == 0
