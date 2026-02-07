"""Unit tests for extract_worker module."""

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.application.workers.runtime import _run_worker_pool
from src.application.workers.workers import (
    Channels,
    ExtractTask,
    _build_knowledge_extraction_graph,
    create_extract_worker,
)


class TestBuildKnowledgeExtractionGraph:
    """Test the _build_knowledge_extraction_graph function."""

    def test_build_knowledge_extraction_graph_returns_compiled_graph(self):
        """Should return a compiled LangGraph."""
        with patch("src.application.workers.workers.NewAI") as mock_ai:
            mock_llm = MagicMock()
            mock_ai.return_value.build.return_value = mock_llm

            graph = _build_knowledge_extraction_graph()

            assert graph is not None
            mock_ai.assert_called_once()


class TestCreateExtractWorker:
    """Test the create_extract_worker function."""

    @pytest.mark.asyncio
    async def test_worker_processes_task(self):
        """Should process a task from the extract queue."""
        channels = Channels()
        task = ExtractTask(area_id=uuid.uuid4(), user_id=uuid.uuid4())
        await channels.extract.put(task)

        with patch(
            "src.application.workers.workers._build_knowledge_extraction_graph"
        ) as mock_build:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock()
            mock_build.return_value = mock_graph

            worker_fn = create_extract_worker(channels)
            worker = asyncio.create_task(worker_fn(0))

            # Wait for task to be processed
            await channels.extract.join()

            worker.cancel()
            try:
                await worker
            except asyncio.CancelledError:
                pass

            mock_graph.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_worker_handles_exception(self):
        """Should continue processing after an exception."""
        channels = Channels()
        task1 = ExtractTask(area_id=uuid.uuid4(), user_id=uuid.uuid4())
        task2 = ExtractTask(area_id=uuid.uuid4(), user_id=uuid.uuid4())
        await channels.extract.put(task1)
        await channels.extract.put(task2)

        with patch(
            "src.application.workers.workers._build_knowledge_extraction_graph"
        ) as mock_build:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(
                side_effect=[Exception("First failed"), None]
            )
            mock_build.return_value = mock_graph

            worker_fn = create_extract_worker(channels)
            worker = asyncio.create_task(worker_fn(0))

            await channels.extract.join()

            worker.cancel()
            try:
                await worker
            except asyncio.CancelledError:
                pass

            assert mock_graph.ainvoke.call_count == 2

    @pytest.mark.asyncio
    async def test_worker_invokes_with_correct_state(self):
        """Should invoke graph with KnowledgeExtractionState containing area_id and user_id."""
        channels = Channels()
        area_id = uuid.uuid4()
        user_id = uuid.uuid4()
        await channels.extract.put(ExtractTask(area_id=area_id, user_id=user_id))

        with patch(
            "src.application.workers.workers._build_knowledge_extraction_graph"
        ) as mock_build:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock()
            mock_build.return_value = mock_graph

            worker = asyncio.create_task(create_extract_worker(channels)(0))
            await channels.extract.join()
            worker.cancel()
            with pytest.raises(asyncio.CancelledError):
                await worker

            call_args = mock_graph.ainvoke.call_args[0][0]
            assert call_args.area_id == area_id
            assert call_args.user_id == user_id


class TestWorkerPool:
    """Test the worker pool functionality."""

    @pytest.mark.asyncio
    async def test_pool_spawns_multiple_workers(self):
        """Should spawn multiple workers that can process tasks concurrently."""
        processed = []

        async def mock_worker(worker_id: int) -> None:
            processed.append(worker_id)
            await asyncio.sleep(0.01)
            raise asyncio.CancelledError()

        pool = asyncio.create_task(_run_worker_pool("test", mock_worker, 3))
        await asyncio.sleep(0.05)

        pool.cancel()
        with pytest.raises(asyncio.CancelledError):
            await pool

        assert sorted(processed) == [0, 1, 2]
