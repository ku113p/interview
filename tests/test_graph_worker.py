"""Unit tests for graph_worker module."""

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.application.workers.channels import ChannelRequest, Channels
from src.application.workers.graph_worker import run_graph_pool
from src.domain import ClientMessage
from src.infrastructure.db import managers as db


async def _create_test_user(temp_db) -> uuid.UUID:
    """Create a test user in the database."""
    user_id = uuid.uuid4()
    await db.UsersManager.create(
        user_id,
        db.User(id=user_id, name="test", mode="auto", current_area_id=None),
    )
    return user_id


def _mock_graph_response(content: str):
    """Create a mock graph that returns the given content."""
    mock_graph = MagicMock()
    mock_graph.ainvoke = AsyncMock(
        return_value={
            "messages": [MagicMock(content=content)],
            "is_fully_covered": False,
        }
    )
    return mock_graph


class TestGraphWorker:
    """Test the graph worker functionality."""

    @pytest.mark.asyncio
    async def test_worker_processes_request_and_sends_response(self, temp_db):
        """Should process a request and send response with matching correlation_id."""
        user_id = await _create_test_user(temp_db)
        channels = Channels()
        corr_id = uuid.uuid4()
        await channels.requests.put(
            ChannelRequest(corr_id, user_id, ClientMessage(data="Hello"))
        )

        with patch("src.application.workers.graph_worker.get_graph") as mock_get:
            mock_get.return_value = _mock_graph_response("Response text")
            pool = asyncio.create_task(run_graph_pool(channels))
            await channels.requests.join()
            response = await asyncio.wait_for(channels.responses.get(), timeout=1.0)
            channels.shutdown.set()
            await asyncio.wait_for(pool, timeout=2.0)

            assert response.correlation_id == corr_id
            assert response.response_text == "Response text"

    @pytest.mark.asyncio
    async def test_worker_handles_multiple_requests(self, temp_db):
        """Should process multiple requests and match responses by correlation_id."""
        user_id = await _create_test_user(temp_db)
        channels = Channels()
        corr_ids = [uuid.uuid4(), uuid.uuid4()]

        for i, corr_id in enumerate(corr_ids):
            await channels.requests.put(
                ChannelRequest(corr_id, user_id, ClientMessage(data=f"Message {i}"))
            )

        with patch("src.application.workers.graph_worker.get_graph") as mock_get:
            counter = [0]

            async def mock_invoke(state):
                idx = counter[0]
                counter[0] += 1
                return {
                    "messages": [MagicMock(content=f"Reply {idx}")],
                    "is_fully_covered": False,
                }

            mock_get.return_value = MagicMock(ainvoke=mock_invoke)
            pool = asyncio.create_task(run_graph_pool(channels))
            await channels.requests.join()
            responses = [await channels.responses.get() for _ in range(2)]
            channels.shutdown.set()
            await asyncio.wait_for(pool, timeout=2.0)

            resp_by_id = {r.correlation_id: r for r in responses}
            assert corr_ids[0] in resp_by_id
            assert corr_ids[1] in resp_by_id

    @pytest.mark.asyncio
    async def test_worker_handles_error_gracefully(self, temp_db):
        """Should send error response when processing fails."""
        user_id = await _create_test_user(temp_db)
        channels = Channels()
        corr_id = uuid.uuid4()
        await channels.requests.put(
            ChannelRequest(corr_id, user_id, ClientMessage(data="fail"))
        )

        with patch("src.application.workers.graph_worker.get_graph") as mock_get:
            mock_get.return_value = MagicMock(
                ainvoke=AsyncMock(side_effect=Exception("Graph failed"))
            )
            pool = asyncio.create_task(run_graph_pool(channels))
            await channels.requests.join()
            response = await asyncio.wait_for(channels.responses.get(), timeout=1.0)
            channels.shutdown.set()
            await asyncio.wait_for(pool, timeout=2.0)

            assert response.correlation_id == corr_id
            assert response.response_text == "An error occurred"
