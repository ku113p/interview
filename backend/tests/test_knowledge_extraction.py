"""Unit tests for knowledge_extraction workflow."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.infrastructure.db import managers as db
from src.shared.ids import new_id
from src.shared.timestamp import get_timestamp
from src.workflows.subgraphs.knowledge_extraction.nodes import (
    KnowledgeExtractionResult,
    KnowledgeItem,
    extract_knowledge,
    load_summary,
    persist_extraction,
    vectorize_summary,
)
from src.workflows.subgraphs.knowledge_extraction.state import KnowledgeExtractionState


class TestLoadSummary:
    """Test the load_summary function."""

    async def test_load_summary_found(self):
        """Should return summary_text, summary_content, and area_id when found."""
        summary_id = new_id()
        area_id = uuid.uuid4()
        mock_summary = db.Summary(
            id=summary_id,
            area_id=area_id,
            summary_text="I'm a software engineer.",
            created_at=1000.0,
        )

        state = KnowledgeExtractionState(summary_id=summary_id)

        with patch.object(
            db.SummariesManager, "get_by_id", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_summary
            result = await load_summary(state)

        assert result["summary_text"] == "I'm a software engineer."
        assert result["summary_content"] == "I'm a software engineer."
        assert result["area_id"] == area_id

    async def test_load_summary_not_found(self):
        """Should return is_successful=False when summary not found."""
        summary_id = new_id()
        state = KnowledgeExtractionState(summary_id=summary_id)

        with patch.object(
            db.SummariesManager, "get_by_id", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = None
            result = await load_summary(state)

        assert result == {}


class TestVectorizeSummary:
    """Test the vectorize_summary function."""

    async def test_vectorize_summary_success(self):
        """Should return summary_vector on success."""
        summary_id = new_id()
        state = KnowledgeExtractionState(
            summary_id=summary_id,
            summary_text="I know Python.",
        )

        mock_embed_client = AsyncMock()
        mock_embed_client.aembed_query.return_value = [0.1, 0.2, 0.3]

        with patch(
            "src.infrastructure.embeddings.get_embedding_client",
            return_value=mock_embed_client,
        ):
            result = await vectorize_summary(state)

        assert result == {"summary_vector": [0.1, 0.2, 0.3]}
        mock_embed_client.aembed_query.assert_called_once_with("I know Python.")

    async def test_vectorize_summary_embedding_failure(self):
        """Should return empty dict when embedding fails."""
        summary_id = new_id()
        state = KnowledgeExtractionState(
            summary_id=summary_id,
            summary_text="I know Python.",
        )

        mock_embed_client = AsyncMock()
        mock_embed_client.aembed_query.side_effect = Exception("Embedding error")

        with patch(
            "src.infrastructure.embeddings.get_embedding_client",
            return_value=mock_embed_client,
        ):
            result = await vectorize_summary(state)

        assert result == {}


class TestExtractKnowledge:
    """Test the extract_knowledge function."""

    async def test_extract_knowledge_skips_when_no_content(self):
        """Should skip extraction when no summary content."""
        state = KnowledgeExtractionState(
            summary_id=new_id(),
            summary_content="",
        )
        mock_llm = MagicMock()

        result = await extract_knowledge(state, mock_llm)

        assert result == {"extracted_knowledge": []}
        mock_llm.with_structured_output.assert_not_called()

    async def test_extract_knowledge_success(self):
        """Should extract knowledge items from summary."""
        state = KnowledgeExtractionState(
            summary_id=new_id(),
            summary_content="Python programming, JavaScript",
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

    async def test_extract_knowledge_handles_exception(self):
        """Should return empty list on LLM exception."""
        state = KnowledgeExtractionState(
            summary_id=new_id(),
            summary_content="Some content",
        )

        mock_structured_llm = AsyncMock()
        mock_structured_llm.ainvoke.side_effect = Exception("LLM error")

        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured_llm

        result = await extract_knowledge(state, mock_llm)

        assert result == {"extracted_knowledge": []}


class TestPersistExtraction:
    """Test the persist_extraction function."""

    async def test_persist_extraction_saves_vector_and_knowledge(self, temp_db):
        """Should write vector to summary and save knowledge items."""
        area_id = uuid.uuid4()
        user_id = uuid.uuid4()
        now = get_timestamp()

        area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)

        summary_id = await db.SummariesManager.create_summary(
            area_id=area_id,
            summary_text="I know Python.",
            created_at=now,
        )

        state = KnowledgeExtractionState(
            summary_id=summary_id,
            summary_text="I know Python.",
            summary_content="I know Python.",
            area_id=area_id,
            summary_vector=[0.1, 0.2, 0.3],
            extracted_knowledge=[
                {"content": "Python", "kind": "skill", "confidence": 0.9},
                {"content": "Works at Google", "kind": "fact", "confidence": 1.0},
            ],
        )

        result = await persist_extraction(state)
        assert result == {}

        updated = await db.SummariesManager.get_by_id(summary_id)
        assert updated.vector == [0.1, 0.2, 0.3]

        all_knowledge = await db.UserKnowledgeManager.list()
        assert len(all_knowledge) == 2
        assert all(k.summary_id == summary_id for k in all_knowledge)

    async def test_persist_extraction_skips_knowledge_when_no_area_id(self, temp_db):
        """Should skip knowledge save when area_id is None."""
        area_id = uuid.uuid4()
        user_id = uuid.uuid4()
        now = get_timestamp()

        area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)

        summary_id = await db.SummariesManager.create_summary(
            area_id=area_id,
            summary_text="I know Python.",
            created_at=now,
        )

        state = KnowledgeExtractionState(
            summary_id=summary_id,
            summary_text="I know Python.",
            summary_content="I know Python.",
            area_id=None,
            extracted_knowledge=[
                {"content": "Python", "kind": "skill", "confidence": 0.9},
            ],
        )

        await persist_extraction(state)

        all_knowledge = await db.UserKnowledgeManager.list()
        assert len(all_knowledge) == 0

    async def test_persist_extraction_rolls_back_on_failure(self, temp_db):
        """Should roll back all writes if update_vector fails."""
        area_id = uuid.uuid4()
        user_id = uuid.uuid4()
        now = get_timestamp()

        area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)

        summary_id = await db.SummariesManager.create_summary(
            area_id=area_id,
            summary_text="I know Python.",
            created_at=now,
        )

        state = KnowledgeExtractionState(
            summary_id=summary_id,
            summary_text="I know Python.",
            summary_content="I know Python.",
            area_id=area_id,
            summary_vector=[0.1, 0.2, 0.3],
            extracted_knowledge=[
                {"content": "Python", "kind": "skill", "confidence": 0.9},
            ],
        )

        with patch.object(
            db.SummariesManager,
            "update_vector",
            side_effect=RuntimeError("simulated failure"),
        ):
            with pytest.raises(RuntimeError, match="simulated failure"):
                await persist_extraction(state)

        all_knowledge = await db.UserKnowledgeManager.list()
        assert len(all_knowledge) == 0

        summary = await db.SummariesManager.get_by_id(summary_id)
        assert summary is not None and summary.vector is None


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


class TestKnowledgeExtractionGraphIntegration:
    """Integration tests for the full knowledge_extraction graph."""

    async def test_full_graph_extracts_and_saves_data(self, temp_db):
        """Test full graph flow: load_summary → vectorize → extract → persist."""
        from src.workflows.subgraphs.knowledge_extraction.graph import (
            build_knowledge_extraction_graph,
        )

        area_id, user_id = uuid.uuid4(), uuid.uuid4()
        now = get_timestamp()

        area = db.LifeArea(
            id=area_id, title="Skills", parent_id=None, user_id=user_id, covered_at=now
        )
        await db.LifeAreasManager.create(area_id, area)

        summary_id = await db.SummariesManager.create_summary(
            area_id=area_id,
            summary_text="Proficient in Python and JavaScript. Aspires to be tech lead.",
            created_at=now,
        )

        mock_embed_client = AsyncMock()
        mock_embed_client.aembed_query.return_value = [0.1, 0.2, 0.3]

        with patch(
            "src.infrastructure.embeddings.get_embedding_client",
            return_value=mock_embed_client,
        ):
            graph = build_knowledge_extraction_graph(llm=_create_knowledge_mock_llm())
            await graph.ainvoke(KnowledgeExtractionState(summary_id=summary_id))

        updated = await db.SummariesManager.get_by_id(summary_id)
        assert updated.vector == [0.1, 0.2, 0.3]

        all_knowledge = await db.UserKnowledgeManager.list()
        assert len(all_knowledge) == 3
        assert all(k.summary_id == summary_id for k in all_knowledge)

    async def test_graph_handles_embedding_failure_gracefully(self, temp_db):
        """Test that graph continues extracting knowledge when embedding fails."""
        from src.workflows.subgraphs.knowledge_extraction.graph import (
            build_knowledge_extraction_graph,
        )

        area_id, user_id = uuid.uuid4(), uuid.uuid4()
        now = get_timestamp()

        area = db.LifeArea(
            id=area_id, title="Skills", parent_id=None, user_id=user_id, covered_at=now
        )
        await db.LifeAreasManager.create(area_id, area)

        summary_id = await db.SummariesManager.create_summary(
            area_id=area_id, summary_text="Knows Python", created_at=now
        )

        mock_embed_client = AsyncMock()
        mock_embed_client.aembed_query.side_effect = Exception("Embedding service down")

        with patch(
            "src.infrastructure.embeddings.get_embedding_client",
            return_value=mock_embed_client,
        ):
            graph = build_knowledge_extraction_graph(llm=_create_knowledge_mock_llm())
            await graph.ainvoke(KnowledgeExtractionState(summary_id=summary_id))

        updated = await db.SummariesManager.get_by_id(summary_id)
        assert updated.vector is None

        # Knowledge extraction still proceeds even without vector
        all_knowledge = await db.UserKnowledgeManager.list()
        assert len(all_knowledge) == 3

    async def test_graph_skips_when_summary_not_found(self, temp_db):
        """Test that graph exits early when summary_id is not in DB."""
        from src.workflows.subgraphs.knowledge_extraction.graph import (
            build_knowledge_extraction_graph,
        )

        summary_id = new_id()
        mock_llm = MagicMock()
        graph = build_knowledge_extraction_graph(llm=mock_llm)
        await graph.ainvoke(KnowledgeExtractionState(summary_id=summary_id))

        mock_llm.with_structured_output.assert_not_called()
        all_knowledge = await db.UserKnowledgeManager.list()
        assert len(all_knowledge) == 0
