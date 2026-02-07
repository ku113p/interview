"""Unit tests for task_processor module."""

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.application.task_processor import (
    _process_queue_item,
    build_extract_graph,
    process_extract_task,
    run_task_processor,
)
from src.domain import ExtractDataTask


class TestBuildExtractGraph:
    """Test the build_extract_graph function."""

    def test_build_extract_graph_returns_compiled_graph(self):
        """Should return a compiled LangGraph."""
        with patch("src.application.task_processor.NewAI") as mock_ai:
            mock_llm = MagicMock()
            mock_ai.return_value.build.return_value = mock_llm

            graph = build_extract_graph()

            assert graph is not None
            mock_ai.assert_called_once()


class TestProcessExtractTask:
    """Test the process_extract_task function."""

    @pytest.mark.asyncio
    async def test_process_extract_task_invokes_graph(self):
        """Should invoke the graph with correct state."""
        area_id = uuid.uuid4()
        user_id = uuid.uuid4()
        task = ExtractDataTask(area_id=area_id, user_id=user_id)

        mock_graph = MagicMock()
        mock_graph.ainvoke = AsyncMock()

        await process_extract_task(mock_graph, task)

        mock_graph.ainvoke.assert_called_once()
        call_args = mock_graph.ainvoke.call_args[0][0]
        assert call_args.area_id == area_id
        assert call_args.user_id == user_id


class TestProcessQueueItem:
    """Test the _process_queue_item function."""

    @pytest.mark.asyncio
    async def test_process_queue_item_returns_true_on_success(self):
        """Should return True after processing a task."""
        queue: asyncio.Queue[ExtractDataTask] = asyncio.Queue()
        task = ExtractDataTask(area_id=uuid.uuid4(), user_id=uuid.uuid4())
        await queue.put(task)

        mock_graph = MagicMock()
        mock_graph.ainvoke = AsyncMock()

        result = await _process_queue_item(mock_graph, queue)

        assert result is True
        assert queue.empty()

    @pytest.mark.asyncio
    async def test_process_queue_item_returns_true_on_exception(self):
        """Should return True even when task processing fails."""
        queue: asyncio.Queue[ExtractDataTask] = asyncio.Queue()
        task = ExtractDataTask(area_id=uuid.uuid4(), user_id=uuid.uuid4())
        await queue.put(task)

        mock_graph = MagicMock()
        mock_graph.ainvoke = AsyncMock(side_effect=Exception("Processing failed"))

        result = await _process_queue_item(mock_graph, queue)

        assert result is True
        assert queue.empty()

    @pytest.mark.asyncio
    async def test_process_queue_item_returns_false_on_cancel(self):
        """Should return False when cancelled."""
        queue: asyncio.Queue[ExtractDataTask] = asyncio.Queue()

        mock_graph = MagicMock()

        async def cancel_during_get():
            # Simulate cancellation while waiting on queue
            raise asyncio.CancelledError()

        with patch.object(queue, "get", side_effect=cancel_during_get):
            result = await _process_queue_item(mock_graph, queue)

        assert result is False


class TestRunTaskProcessor:
    """Test the run_task_processor function."""

    @pytest.mark.asyncio
    async def test_run_task_processor_processes_tasks(self):
        """Should process tasks from queue until cancelled."""
        queue: asyncio.Queue[ExtractDataTask] = asyncio.Queue()
        task = ExtractDataTask(area_id=uuid.uuid4(), user_id=uuid.uuid4())
        await queue.put(task)

        with patch("src.application.task_processor.build_extract_graph") as mock_build:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock()
            mock_build.return_value = mock_graph

            # Run processor in background and cancel after task is processed
            processor = asyncio.create_task(run_task_processor(queue))

            # Wait for task to be processed
            await queue.join()

            # Cancel the processor
            processor.cancel()
            try:
                await processor
            except asyncio.CancelledError:
                pass

            mock_graph.ainvoke.assert_called_once()
