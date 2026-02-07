"""Unit tests for Runtime class."""

import asyncio
import uuid
from unittest.mock import patch

import pytest
from src.application.workers import Runtime
from src.application.workers.channels import Channels
from src.domain import ClientMessage, InputMode, User


def _make_graph_worker(channels: Channels, response_fn):
    """Create a test graph worker that uses response_fn to generate responses."""

    async def worker(worker_id: int) -> None:
        while True:
            msg = await channels.client_message.get()
            try:
                response = response_fn(msg)
                await channels.client_response.put(response)
            finally:
                channels.client_message.task_done()

    return worker


def _make_extract_worker(channels: Channels):
    """Create a test extract worker that does nothing."""

    async def worker(worker_id: int) -> None:
        while True:
            await channels.extract.get()
            channels.extract.task_done()

    return worker


class TestRuntime:
    """Test the Runtime class."""

    @pytest.fixture
    def user(self):
        return User(id=uuid.uuid4(), mode=InputMode.auto)

    @pytest.mark.asyncio
    async def test_context_manager_starts_and_stops(self, user):
        """Runtime should start pools on enter and stop on exit."""
        with (
            patch("src.application.workers.runtime.create_graph_worker") as mock_graph,
            patch(
                "src.application.workers.runtime.create_extract_worker"
            ) as mock_extract,
        ):
            mock_graph.side_effect = lambda ch, u: _make_graph_worker(
                ch, lambda m: "ok"
            )
            mock_extract.side_effect = lambda ch: _make_extract_worker(ch)

            async with Runtime(user):
                mock_graph.assert_called_once()
                mock_extract.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_and_receive(self, user):
        """Should send message and receive response."""
        with (
            patch("src.application.workers.runtime.create_graph_worker") as mock_graph,
            patch(
                "src.application.workers.runtime.create_extract_worker"
            ) as mock_extract,
        ):
            mock_graph.side_effect = lambda ch, u: _make_graph_worker(
                ch, lambda m: f"Response to: {m.data}"
            )
            mock_extract.side_effect = lambda ch: _make_extract_worker(ch)

            async with Runtime(user) as runtime:
                msg = ClientMessage(data="Hello")
                response = await asyncio.wait_for(
                    runtime.send_and_receive(msg), timeout=1.0
                )
                assert response == "Response to: Hello"

    @pytest.mark.asyncio
    async def test_multiple_messages(self, user):
        """Should handle multiple messages in sequence."""
        with (
            patch("src.application.workers.runtime.create_graph_worker") as mock_graph,
            patch(
                "src.application.workers.runtime.create_extract_worker"
            ) as mock_extract,
        ):
            counter = [0]

            def make_response(msg):
                counter[0] += 1
                return f"Msg #{counter[0]}"

            mock_graph.side_effect = lambda ch, u: _make_graph_worker(ch, make_response)
            mock_extract.side_effect = lambda ch: _make_extract_worker(ch)

            async with Runtime(user) as runtime:
                r1 = await asyncio.wait_for(
                    runtime.send_and_receive(ClientMessage(data="a")), timeout=1.0
                )
                r2 = await asyncio.wait_for(
                    runtime.send_and_receive(ClientMessage(data="b")), timeout=1.0
                )

                assert r1 == "Msg #1"
                assert r2 == "Msg #2"
