"""Unit tests for extract_worker module."""

import asyncio
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


class TestExtractWorker:
    """Test the extract worker functionality."""

    @pytest.mark.asyncio
    async def test_worker_processes_task(self):
        """Should process a task from the extract queue."""
        channels = Channels()
        task = ExtractTask(summary_id=new_id())
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
        task1 = ExtractTask(summary_id=new_id())
        task2 = ExtractTask(summary_id=new_id())
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
        """Should invoke graph with KnowledgeExtractionState containing summary_id."""
        channels = Channels()
        summary_id = new_id()
        await channels.extract.put(ExtractTask(summary_id=summary_id))

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
            assert call_args.summary_id == summary_id


async def _create_summary_for_extraction(user_id, area_id):
    """Helper to create a leaf area with a summary in summaries table."""
    now = get_timestamp()
    area = db.LifeArea(
        id=area_id, title="Skills", parent_id=None, user_id=user_id, covered_at=now
    )
    await db.LifeAreasManager.create(area_id, area)

    summary_id = await db.SummariesManager.create_summary(
        area_id=area_id,
        summary_text="Proficient in Python with 5 years experience",
        created_at=now,
    )
    return summary_id


def _create_extraction_mock_llm():
    """Create mock LLM returning sample knowledge items."""
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

    mock_knowledge_llm = AsyncMock()
    mock_knowledge_llm.ainvoke.return_value = knowledge_result

    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_knowledge_llm
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


async def _verify_extraction_results(area_id, user_id, summary_id):
    """Verify extraction wrote vector, created knowledge with summary_id."""
    updated = await db.SummariesManager.get_by_id(summary_id)
    assert updated.vector == [0.1, 0.2, 0.3]

    all_knowledge = await db.UserKnowledgeManager.list()
    assert len(all_knowledge) == 2
    descriptions = [k.description for k in all_knowledge]
    assert "Proficient in Python" in descriptions
    assert "5 years programming experience" in descriptions
    assert all(k.summary_id == summary_id for k in all_knowledge)


class TestFullSummaryExtractionFlow:
    """Integration tests for the complete per-summary extraction flow."""

    @pytest.mark.asyncio
    async def test_full_summary_extraction_flow(self, temp_db):
        """Integration test: summary saved → extract queued → knowledge extracted."""
        user_id, area_id = new_id(), new_id()
        summary_id = await _create_summary_for_extraction(user_id, area_id)

        channels = Channels()
        await channels.extract.put(ExtractTask(summary_id=summary_id))

        await _run_extract_pool_with_mocks(channels, _create_extraction_mock_llm())
        await _verify_extraction_results(area_id, user_id, summary_id)


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
