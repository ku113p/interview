"""Unit tests for interview-specific database managers."""

import uuid

import pytest
from src.infrastructure.db import managers as db
from src.shared.ids import new_id
from src.shared.timestamp import get_timestamp


async def _create_leaf_messages(
    user_id: uuid.UUID, leaf_id: uuid.UUID, now: float
) -> list[uuid.UUID]:
    """Create two messages linked to leaf_id and return their IDs."""
    created_ids = []
    for i, (role, content) in enumerate(
        [("assistant", "What is your experience?"), ("user", "Five years.")]
    ):
        history_id = new_id()
        created_ids.append(history_id)
        history = db.History(
            id=history_id,
            message_data={"role": role, "content": content},
            user_id=user_id,
            created_ts=now + i,
        )
        await db.HistoriesManager.create(history_id, history)
        await db.LeafHistoryManager.link(leaf_id, history_id)
    return created_ids


class TestSummariesManager:
    """Tests for SummariesManager."""

    @pytest.mark.asyncio
    async def test_create_and_get_by_id(self, temp_db):
        """Should create and retrieve a summary record."""
        area_id = new_id()
        now = get_timestamp()

        summary_id = await db.SummariesManager.create_summary(
            area_id=area_id,
            summary_text="User has 5 years of Python experience.",
            created_at=now,
        )

        result = await db.SummariesManager.get_by_id(summary_id)
        assert result is not None
        assert result.id == summary_id
        assert result.area_id == area_id
        assert result.summary_text == "User has 5 years of Python experience."
        assert result.vector is None

    @pytest.mark.asyncio
    async def test_list_by_area(self, temp_db):
        """Should list all summaries for an area in creation order."""
        area_id = new_id()
        now = get_timestamp()

        id1 = await db.SummariesManager.create_summary(
            area_id=area_id, summary_text="First summary.", created_at=now
        )
        id2 = await db.SummariesManager.create_summary(
            area_id=area_id, summary_text="Second summary.", created_at=now + 1
        )

        results = await db.SummariesManager.list_by_area(area_id)
        assert len(results) == 2
        assert results[0].id == id1
        assert results[1].id == id2

    @pytest.mark.asyncio
    async def test_list_by_area_empty(self, temp_db):
        """Should return empty list for area with no summaries."""
        area_id = new_id()
        results = await db.SummariesManager.list_by_area(area_id)
        assert results == []

    @pytest.mark.asyncio
    async def test_update_vector(self, temp_db):
        """Should save embedding vector to a summary."""
        area_id = new_id()
        now = get_timestamp()

        summary_id = await db.SummariesManager.create_summary(
            area_id=area_id, summary_text="Summary text.", created_at=now
        )

        vector = [0.1, 0.2, 0.3]
        await db.SummariesManager.update_vector(summary_id, vector)

        result = await db.SummariesManager.get_by_id(summary_id)
        assert result.vector == vector

    @pytest.mark.asyncio
    async def test_delete_by_area(self, temp_db):
        """Should delete all summaries for an area."""
        area_id = new_id()
        other_area_id = new_id()
        now = get_timestamp()

        await db.SummariesManager.create_summary(
            area_id=area_id, summary_text="Summary 1.", created_at=now
        )
        await db.SummariesManager.create_summary(
            area_id=area_id, summary_text="Summary 2.", created_at=now + 1
        )
        await db.SummariesManager.create_summary(
            area_id=other_area_id, summary_text="Other area.", created_at=now
        )

        await db.SummariesManager.delete_by_area(area_id)

        deleted = await db.SummariesManager.list_by_area(area_id)
        assert len(deleted) == 0

        remaining = await db.SummariesManager.list_by_area(other_area_id)
        assert len(remaining) == 1

    @pytest.mark.asyncio
    async def test_create_with_question_and_answer_ids(self, temp_db):
        """Should store question_id and answer_id on summaries."""
        area_id = new_id()
        question_id = new_id()
        answer_id = new_id()
        now = get_timestamp()

        summary_id = await db.SummariesManager.create_summary(
            area_id=area_id,
            summary_text="Summary with references.",
            created_at=now,
            question_id=question_id,
            answer_id=answer_id,
        )

        result = await db.SummariesManager.get_by_id(summary_id)
        assert result.question_id == question_id
        assert result.answer_id == answer_id


class TestLeafHistoryManager:
    """Tests for LeafHistoryManager."""

    @pytest.mark.asyncio
    async def test_link_and_get_messages(self, temp_db):
        """Should link history to leaf and retrieve messages."""
        user_id = new_id()
        leaf_id = new_id()
        history_id = new_id()
        now = get_timestamp()

        # Create history record
        history = db.History(
            id=history_id,
            message_data={"role": "user", "content": "Hello"},
            user_id=user_id,
            created_ts=now,
        )
        await db.HistoriesManager.create(history_id, history)

        # Link to leaf
        await db.LeafHistoryManager.link(leaf_id, history_id)

        # Get messages
        messages = await db.LeafHistoryManager.get_messages(leaf_id)
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"

    @pytest.mark.asyncio
    async def test_get_messages_ordered_by_time(self, temp_db):
        """Should return messages in chronological order."""
        user_id = new_id()
        leaf_id = new_id()
        now = get_timestamp()

        # Create and link multiple messages
        for i, content in enumerate(["First", "Second", "Third"]):
            history_id = new_id()
            history = db.History(
                id=history_id,
                message_data={"role": "user", "content": content},
                user_id=user_id,
                created_ts=now + i,
            )
            await db.HistoriesManager.create(history_id, history)
            await db.LeafHistoryManager.link(leaf_id, history_id)

        messages = await db.LeafHistoryManager.get_messages(leaf_id)
        assert len(messages) == 3
        assert messages[0]["content"] == "First"
        assert messages[1]["content"] == "Second"
        assert messages[2]["content"] == "Third"

    @pytest.mark.asyncio
    async def test_get_message_count(self, temp_db):
        """Should return correct message count for a leaf."""
        user_id = new_id()
        leaf_id = new_id()
        now = get_timestamp()

        # Create and link 3 messages
        for i in range(3):
            history_id = new_id()
            history = db.History(
                id=history_id,
                message_data={"role": "user", "content": f"Message {i}"},
                user_id=user_id,
                created_ts=now + i,
            )
            await db.HistoriesManager.create(history_id, history)
            await db.LeafHistoryManager.link(leaf_id, history_id)

        count = await db.LeafHistoryManager.get_message_count(leaf_id)
        assert count == 3

    @pytest.mark.asyncio
    async def test_delete_by_leaf(self, temp_db):
        """Should delete all history links for a leaf."""
        user_id = new_id()
        leaf_id = new_id()
        history_id = new_id()
        now = get_timestamp()

        # Create and link history
        history = db.History(
            id=history_id,
            message_data={"role": "user", "content": "Test"},
            user_id=user_id,
            created_ts=now,
        )
        await db.HistoriesManager.create(history_id, history)
        await db.LeafHistoryManager.link(leaf_id, history_id)

        # Delete links
        await db.LeafHistoryManager.delete_by_leaf(leaf_id)

        # Verify links deleted
        messages = await db.LeafHistoryManager.get_messages(leaf_id)
        assert len(messages) == 0

    @pytest.mark.asyncio
    async def test_link_ignores_duplicate(self, temp_db):
        """Should ignore duplicate links (INSERT OR IGNORE)."""
        user_id = new_id()
        leaf_id = new_id()
        history_id = new_id()
        now = get_timestamp()

        # Create history
        history = db.History(
            id=history_id,
            message_data={"role": "user", "content": "Test"},
            user_id=user_id,
            created_ts=now,
        )
        await db.HistoriesManager.create(history_id, history)

        # Link twice (should not raise)
        await db.LeafHistoryManager.link(leaf_id, history_id)
        await db.LeafHistoryManager.link(leaf_id, history_id)

        # Should still only have one message
        count = await db.LeafHistoryManager.get_message_count(leaf_id)
        assert count == 1

    @pytest.mark.asyncio
    async def test_get_messages_with_ids(self, temp_db):
        """Should return (uuid, dict) pairs in chronological order."""
        import uuid as uuid_module

        user_id, leaf_id = new_id(), new_id()
        now = get_timestamp()
        created_ids = await _create_leaf_messages(user_id, leaf_id, now)

        results = await db.LeafHistoryManager.get_messages_with_ids(leaf_id)

        assert len(results) == 2
        msg_id0, msg0 = results[0]
        msg_id1, msg1 = results[1]
        assert isinstance(msg_id0, uuid_module.UUID)
        assert isinstance(msg0, dict)
        assert msg_id0 == created_ids[0]
        assert msg0["content"] == "What is your experience?"
        assert msg_id1 == created_ids[1]
        assert msg1["content"] == "Five years."
