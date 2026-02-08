"""Unit tests for extract_worker module."""

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.application.workers.channels import Channels, ExtractTask
from src.application.workers.extract_worker import run_extract_pool
from src.application.workers.pool import run_worker_pool


class TestExtractWorker:
    """Test the extract worker functionality."""

    @pytest.mark.asyncio
    async def test_worker_processes_task(self):
        """Should process a task from the extract queue."""
        channels = Channels()
        task = ExtractTask(area_id=uuid.uuid4(), user_id=uuid.uuid4())
        await channels.extract.put(task)

        with (
            patch("src.application.workers.extract_worker.LLMClientBuilder") as mock_ai,
            patch(
                "src.application.workers.extract_worker.build_knowledge_extraction_graph"
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
        task1 = ExtractTask(area_id=uuid.uuid4(), user_id=uuid.uuid4())
        task2 = ExtractTask(area_id=uuid.uuid4(), user_id=uuid.uuid4())
        await channels.extract.put(task1)
        await channels.extract.put(task2)

        with (
            patch("src.application.workers.extract_worker.LLMClientBuilder") as mock_ai,
            patch(
                "src.application.workers.extract_worker.build_knowledge_extraction_graph"
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
        """Should invoke graph with KnowledgeExtractionState containing area_id and user_id."""
        channels = Channels()
        area_id = uuid.uuid4()
        user_id = uuid.uuid4()
        await channels.extract.put(ExtractTask(area_id=area_id, user_id=user_id))

        with (
            patch("src.application.workers.extract_worker.LLMClientBuilder") as mock_ai,
            patch(
                "src.application.workers.extract_worker.build_knowledge_extraction_graph"
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
            assert call_args.user_id == user_id


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
