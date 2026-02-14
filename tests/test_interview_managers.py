"""Unit tests for interview-specific database managers."""

import pytest
from src.infrastructure.db import managers as db
from src.shared.ids import new_id
from src.shared.timestamp import get_timestamp


class TestLeafCoverageManager:
    """Tests for LeafCoverageManager."""

    @pytest.mark.asyncio
    async def test_create_and_get_by_id(self, temp_db):
        """Should create and retrieve a leaf coverage record."""
        leaf_id, root_area_id = new_id(), new_id()
        now = get_timestamp()

        coverage = db.LeafCoverage(
            leaf_id=leaf_id,
            root_area_id=root_area_id,
            status="pending",
            updated_at=now,
        )
        await db.LeafCoverageManager.create(leaf_id, coverage)

        result = await db.LeafCoverageManager.get_by_id(leaf_id)
        assert result is not None
        assert result.leaf_id == leaf_id
        assert result.status == "pending"

    @pytest.mark.asyncio
    async def test_list_by_root_area(self, temp_db):
        """Should list all coverage records for a root area."""
        root_area_id = new_id()
        leaf1_id, leaf2_id = new_id(), new_id()
        now = get_timestamp()

        for leaf_id in [leaf1_id, leaf2_id]:
            coverage = db.LeafCoverage(
                leaf_id=leaf_id,
                root_area_id=root_area_id,
                status="pending",
                updated_at=now,
            )
            await db.LeafCoverageManager.create(leaf_id, coverage)

        result = await db.LeafCoverageManager.list_by_root_area(root_area_id)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_update_status(self, temp_db):
        """Should update the status of a leaf coverage record."""
        leaf_id, root_area_id = new_id(), new_id()
        now = get_timestamp()

        coverage = db.LeafCoverage(
            leaf_id=leaf_id,
            root_area_id=root_area_id,
            status="pending",
            updated_at=now,
        )
        await db.LeafCoverageManager.create(leaf_id, coverage)

        await db.LeafCoverageManager.update_status(leaf_id, "covered", now + 1)

        result = await db.LeafCoverageManager.get_by_id(leaf_id)
        assert result.status == "covered"

    @pytest.mark.asyncio
    async def test_save_summary(self, temp_db):
        """Should save summary text and vector."""
        leaf_id, root_area_id = new_id(), new_id()
        now = get_timestamp()

        coverage = db.LeafCoverage(
            leaf_id=leaf_id,
            root_area_id=root_area_id,
            status="covered",
            updated_at=now,
        )
        await db.LeafCoverageManager.create(leaf_id, coverage)

        vector = [0.1, 0.2, 0.3]
        await db.LeafCoverageManager.save_summary(
            leaf_id, "User has Python experience", vector, now + 1
        )

        result = await db.LeafCoverageManager.get_by_id(leaf_id)
        assert result.summary_text == "User has Python experience"
        assert result.vector == vector

    @pytest.mark.asyncio
    async def test_delete_by_root_area(self, temp_db):
        """Should delete all coverage records for a root area."""
        root_area_id = new_id()
        leaf1_id, leaf2_id = new_id(), new_id()
        now = get_timestamp()

        for leaf_id in [leaf1_id, leaf2_id]:
            coverage = db.LeafCoverage(
                leaf_id=leaf_id,
                root_area_id=root_area_id,
                status="pending",
                updated_at=now,
            )
            await db.LeafCoverageManager.create(leaf_id, coverage)

        await db.LeafCoverageManager.delete_by_root_area(root_area_id)

        result = await db.LeafCoverageManager.list_by_root_area(root_area_id)
        assert len(result) == 0


class TestActiveInterviewContextManager:
    """Tests for ActiveInterviewContextManager."""

    @pytest.mark.asyncio
    async def test_create_and_get_by_user(self, temp_db):
        """Should create and retrieve context by user ID."""
        user_id, root_area_id, leaf_id = new_id(), new_id(), new_id()
        now = get_timestamp()

        ctx = db.ActiveInterviewContext(
            user_id=user_id,
            root_area_id=root_area_id,
            active_leaf_id=leaf_id,
            created_at=now,
        )
        await db.ActiveInterviewContextManager.create(user_id, ctx)

        result = await db.ActiveInterviewContextManager.get_by_user(user_id)
        assert result is not None
        assert result.user_id == user_id
        assert result.active_leaf_id == leaf_id

    @pytest.mark.asyncio
    async def test_update_active_leaf(self, temp_db):
        """Should update active leaf."""
        user_id, root_area_id = new_id(), new_id()
        leaf1_id, leaf2_id = new_id(), new_id()
        now = get_timestamp()

        ctx = db.ActiveInterviewContext(
            user_id=user_id,
            root_area_id=root_area_id,
            active_leaf_id=leaf1_id,
            created_at=now,
            question_text="Old question",
        )
        await db.ActiveInterviewContextManager.create(user_id, ctx)

        await db.ActiveInterviewContextManager.update_active_leaf(
            user_id, leaf2_id, "New question"
        )

        result = await db.ActiveInterviewContextManager.get_by_user(user_id)
        assert result.active_leaf_id == leaf2_id
        assert result.question_text == "New question"

    @pytest.mark.asyncio
    async def test_delete_by_user(self, temp_db):
        """Should delete context for a user."""
        user_id, root_area_id, leaf_id = new_id(), new_id(), new_id()
        now = get_timestamp()

        ctx = db.ActiveInterviewContext(
            user_id=user_id,
            root_area_id=root_area_id,
            active_leaf_id=leaf_id,
            created_at=now,
        )
        await db.ActiveInterviewContextManager.create(user_id, ctx)

        await db.ActiveInterviewContextManager.delete_by_user(user_id)

        result = await db.ActiveInterviewContextManager.get_by_user(user_id)
        assert result is None


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
