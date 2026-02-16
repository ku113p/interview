"""Unit tests for extract_worker module."""

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.infrastructure.db import managers as db
from src.processes.extract import ExtractTask, run_extract_pool
from src.runtime import Channels, run_worker_pool
from src.shared.ids import new_id
from src.shared.timestamp import get_timestamp
from src.workflows.subgraphs.knowledge_extraction.knowledge_nodes import (
    KnowledgeExtractionResult,
    KnowledgeItem,
)
from src.workflows.subgraphs.knowledge_extraction.nodes import (
    ExtractionResult,
    SubAreaSummary,
)


class TestExtractWorker:
    """Test the extract worker functionality."""

    @pytest.mark.asyncio
    async def test_worker_processes_task(self):
        """Should process a task from the extract queue."""
        channels = Channels()
        task = ExtractTask(area_id=uuid.uuid4())
        await channels.extract.put(task)

        with (
            patch("src.processes.extract.worker.LLMClientBuilder") as mock_ai,
            patch(
                "src.processes.extract.worker.build_knowledge_extraction_graph"
            ) as mock_build,
        ):
            mock_ai.return_value.build.return_value = MagicMock()
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock()
            mock_build.return_value = mock_graph

            pool = asyncio.create_task(run_extract_pool(channels))

            # Wait for task to be processed
            await channels.extract.join()

            # Signal shutdown and wait for pool to stop
            channels.shutdown.set()
            await asyncio.wait_for(pool, timeout=2.0)

            mock_graph.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_worker_handles_exception(self):
        """Should continue processing after an exception."""
        channels = Channels()
        task1 = ExtractTask(area_id=uuid.uuid4())
        task2 = ExtractTask(area_id=uuid.uuid4())
        await channels.extract.put(task1)
        await channels.extract.put(task2)

        with (
            patch("src.processes.extract.worker.LLMClientBuilder") as mock_ai,
            patch(
                "src.processes.extract.worker.build_knowledge_extraction_graph"
            ) as mock_build,
        ):
            mock_ai.return_value.build.return_value = MagicMock()
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(
                side_effect=[Exception("First failed"), None]
            )
            mock_build.return_value = mock_graph

            pool = asyncio.create_task(run_extract_pool(channels))

            await channels.extract.join()

            channels.shutdown.set()
            await asyncio.wait_for(pool, timeout=2.0)

            assert mock_graph.ainvoke.call_count == 2

    @pytest.mark.asyncio
    async def test_worker_invokes_with_correct_state(self):
        """Should invoke graph with KnowledgeExtractionState containing area_id."""
        channels = Channels()
        area_id = uuid.uuid4()
        await channels.extract.put(ExtractTask(area_id=area_id))

        with (
            patch("src.processes.extract.worker.LLMClientBuilder") as mock_ai,
            patch(
                "src.processes.extract.worker.build_knowledge_extraction_graph"
            ) as mock_build,
        ):
            mock_ai.return_value.build.return_value = MagicMock()
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock()
            mock_build.return_value = mock_graph

            pool = asyncio.create_task(run_extract_pool(channels))
            await channels.extract.join()
            channels.shutdown.set()
            await asyncio.wait_for(pool, timeout=2.0)

            call_args = mock_graph.ainvoke.call_args[0][0]
            assert call_args.area_id == area_id


async def _create_leaf_with_messages(user_id, area_id):
    """Helper to create a leaf area with summary in leaf_coverage."""
    area = db.LifeArea(id=area_id, title="Skills", parent_id=None, user_id=user_id)
    await db.LifeAreasManager.create(area_id, area)

    now = get_timestamp()
    # Create leaf coverage with summary (as the main graph would)
    coverage = db.LeafCoverage(
        leaf_id=area_id,
        root_area_id=area_id,
        status="covered",
        summary_text="Proficient in Python with 5 years experience",
        updated_at=now,
    )
    await db.LeafCoverageManager.create(area_id, coverage)


def _create_extraction_mock_llm():
    """Create mock LLM that handles both summary and knowledge extraction."""
    summary_result = ExtractionResult(
        summaries=[
            SubAreaSummary(
                sub_area="Skills",
                summary="Proficient in Python with 5 years experience",
            )
        ]
    )
    knowledge_result = KnowledgeExtractionResult(
        items=[
            KnowledgeItem(
                content="Proficient in Python", kind="skill", confidence=0.95
            ),
            KnowledgeItem(
                content="5 years programming experience", kind="fact", confidence=0.9
            ),
        ]
    )

    mock_summary_llm = AsyncMock()
    mock_summary_llm.ainvoke.return_value = summary_result
    mock_knowledge_llm = AsyncMock()
    mock_knowledge_llm.ainvoke.return_value = knowledge_result

    def mock_with_structured_output(schema):
        return mock_summary_llm if schema == ExtractionResult else mock_knowledge_llm

    mock_llm = MagicMock()
    mock_llm.with_structured_output.side_effect = mock_with_structured_output
    return mock_llm


async def _run_extract_pool_with_mocks(channels, mock_llm):
    """Run extract pool with mocked LLM and embeddings."""
    mock_embed_client = AsyncMock()
    mock_embed_client.aembed_query.return_value = [0.1, 0.2, 0.3]

    with (
        patch("src.processes.extract.worker.LLMClientBuilder") as mock_builder,
        patch(
            "src.infrastructure.embeddings.get_embedding_client",
            return_value=mock_embed_client,
        ),
    ):
        mock_builder.return_value.build.return_value = mock_llm
        pool = asyncio.create_task(run_extract_pool(channels))
        await channels.extract.join()
        channels.shutdown.set()
        await asyncio.wait_for(pool, timeout=5.0)


async def _verify_extraction_results(area_id, user_id):
    """Verify extraction created knowledge, links, and marked area extracted."""
    all_knowledge = await db.UserKnowledgeManager.list()
    assert len(all_knowledge) == 2
    descriptions = [k.description for k in all_knowledge]
    assert "Proficient in Python" in descriptions
    assert "5 years programming experience" in descriptions

    links = await db.UserKnowledgeAreasManager.list_by_user(user_id)
    assert len(links) == 2
    assert all(link.area_id == area_id for link in links)

    # Area should be marked as extracted
    area = await db.LifeAreasManager.get_by_id(area_id)
    assert area.extracted_at is not None


class TestFullLeafExtractionFlow:
    """Integration tests for the complete leaf extraction flow."""

    @pytest.mark.asyncio
    async def test_full_leaf_extraction_flow(self, temp_db):
        """Integration test: leaf messages → extract queued → knowledge extracted."""
        user_id, area_id = new_id(), new_id()
        await _create_leaf_with_messages(user_id, area_id)

        channels = Channels()
        await channels.extract.put(ExtractTask(area_id=area_id))

        await _run_extract_pool_with_mocks(channels, _create_extraction_mock_llm())
        await _verify_extraction_results(area_id, user_id)


class TestWorkerPool:
    """Test the worker pool functionality."""

    @pytest.mark.asyncio
    async def test_pool_spawns_multiple_workers(self):
        """Should spawn multiple workers that can process tasks concurrently."""
        processed = []
        shutdown = asyncio.Event()

        async def mock_worker(worker_id: int) -> None:
            processed.append(worker_id)
            while not shutdown.is_set():
                await asyncio.sleep(0.01)

        pool = asyncio.create_task(run_worker_pool("test", mock_worker, 3, shutdown))
        await asyncio.sleep(0.05)

        shutdown.set()
        await asyncio.wait_for(pool, timeout=2.0)

        assert sorted(processed) == [0, 1, 2]
