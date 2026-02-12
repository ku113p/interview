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
            message_ids=["msg1", "msg2"],
        )
        await db.ActiveInterviewContextManager.create(user_id, ctx)

        result = await db.ActiveInterviewContextManager.get_by_user(user_id)
        assert result is not None
        assert result.user_id == user_id
        assert result.active_leaf_id == leaf_id
        assert result.message_ids == ["msg1", "msg2"]

    @pytest.mark.asyncio
    async def test_update_message_ids(self, temp_db):
        """Should update message_ids list."""
        user_id, root_area_id, leaf_id = new_id(), new_id(), new_id()
        now = get_timestamp()

        ctx = db.ActiveInterviewContext(
            user_id=user_id,
            root_area_id=root_area_id,
            active_leaf_id=leaf_id,
            created_at=now,
            message_ids=[],
        )
        await db.ActiveInterviewContextManager.create(user_id, ctx)

        await db.ActiveInterviewContextManager.update_message_ids(
            user_id, ["msg1", "msg2", "msg3"]
        )

        result = await db.ActiveInterviewContextManager.get_by_user(user_id)
        assert result.message_ids == ["msg1", "msg2", "msg3"]

    @pytest.mark.asyncio
    async def test_update_active_leaf(self, temp_db):
        """Should update active leaf and reset message_ids."""
        user_id, root_area_id = new_id(), new_id()
        leaf1_id, leaf2_id = new_id(), new_id()
        now = get_timestamp()

        ctx = db.ActiveInterviewContext(
            user_id=user_id,
            root_area_id=root_area_id,
            active_leaf_id=leaf1_id,
            created_at=now,
            message_ids=["old_msg"],
            question_text="Old question",
        )
        await db.ActiveInterviewContextManager.create(user_id, ctx)

        await db.ActiveInterviewContextManager.update_active_leaf(
            user_id, leaf2_id, "New question"
        )

        result = await db.ActiveInterviewContextManager.get_by_user(user_id)
        assert result.active_leaf_id == leaf2_id
        assert result.question_text == "New question"
        assert result.message_ids == []  # Reset

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


class TestLeafExtractionQueueManager:
    """Tests for LeafExtractionQueueManager."""

    @pytest.mark.asyncio
    async def test_create_and_claim_pending(self, temp_db):
        """Should create task and claim it atomically."""
        task_id, leaf_id, root_area_id = new_id(), new_id(), new_id()
        now = get_timestamp()

        task = db.LeafExtractionQueueItem(
            id=task_id,
            leaf_id=leaf_id,
            root_area_id=root_area_id,
            message_ids=["msg1"],
            created_at=now,
        )
        await db.LeafExtractionQueueManager.create(task_id, task)

        # Claim the task
        claimed = await db.LeafExtractionQueueManager.claim_pending(limit=1)
        assert len(claimed) == 1
        assert claimed[0].id == task_id
        assert claimed[0].status == "pending"  # Status in returned object

        # Verify it's now processing in DB
        # Try to claim again - should get nothing
        claimed_again = await db.LeafExtractionQueueManager.claim_pending(limit=1)
        assert len(claimed_again) == 0

    @pytest.mark.asyncio
    async def test_claim_pending_batch(self, temp_db):
        """Should claim multiple tasks in one call."""
        root_area_id = new_id()
        now = get_timestamp()

        # Create 3 tasks
        for i in range(3):
            task = db.LeafExtractionQueueItem(
                id=new_id(),
                leaf_id=new_id(),
                root_area_id=root_area_id,
                message_ids=["msg"],
                created_at=now + i,
            )
            await db.LeafExtractionQueueManager.create(task.id, task)

        # Claim 2
        claimed = await db.LeafExtractionQueueManager.claim_pending(limit=2)
        assert len(claimed) == 2

        # 1 should remain
        remaining = await db.LeafExtractionQueueManager.claim_pending(limit=5)
        assert len(remaining) == 1

    @pytest.mark.asyncio
    async def test_mark_completed(self, temp_db):
        """Should mark task as completed with timestamp."""
        task_id, leaf_id, root_area_id = new_id(), new_id(), new_id()
        now = get_timestamp()

        task = db.LeafExtractionQueueItem(
            id=task_id,
            leaf_id=leaf_id,
            root_area_id=root_area_id,
            message_ids=["msg"],
            created_at=now,
        )
        await db.LeafExtractionQueueManager.create(task_id, task)

        completed_at = now + 10
        await db.LeafExtractionQueueManager.mark_completed(task_id, completed_at)

        result = await db.LeafExtractionQueueManager.get_by_id(task_id)
        assert result.status == "completed"
        assert result.processed_at == completed_at

    @pytest.mark.asyncio
    async def test_mark_failed_increments_retry(self, temp_db):
        """Should mark task as failed and increment retry count."""
        task_id, leaf_id, root_area_id = new_id(), new_id(), new_id()
        now = get_timestamp()

        task = db.LeafExtractionQueueItem(
            id=task_id,
            leaf_id=leaf_id,
            root_area_id=root_area_id,
            message_ids=["msg"],
            created_at=now,
        )
        await db.LeafExtractionQueueManager.create(task_id, task)

        await db.LeafExtractionQueueManager.mark_failed(task_id)

        result = await db.LeafExtractionQueueManager.get_by_id(task_id)
        assert result.status == "failed"
        assert result.retry_count == 1

        # Fail again
        await db.LeafExtractionQueueManager.mark_failed(task_id)
        result = await db.LeafExtractionQueueManager.get_by_id(task_id)
        assert result.retry_count == 2

    @pytest.mark.asyncio
    async def test_requeue_failed_under_max_retries(self, temp_db):
        """Should requeue failed tasks under max retries."""
        task_id, leaf_id, root_area_id = new_id(), new_id(), new_id()
        now = get_timestamp()

        task = db.LeafExtractionQueueItem(
            id=task_id,
            leaf_id=leaf_id,
            root_area_id=root_area_id,
            message_ids=["msg"],
            created_at=now,
            status="failed",
            retry_count=2,
        )
        await db.LeafExtractionQueueManager.create(task_id, task)

        # Requeue with max_retries=3
        await db.LeafExtractionQueueManager.requeue_failed(max_retries=3)

        result = await db.LeafExtractionQueueManager.get_by_id(task_id)
        assert result.status == "pending"

    @pytest.mark.asyncio
    async def test_requeue_failed_skips_at_max_retries(self, temp_db):
        """Should not requeue tasks at max retries."""
        task_id, leaf_id, root_area_id = new_id(), new_id(), new_id()
        now = get_timestamp()

        task = db.LeafExtractionQueueItem(
            id=task_id,
            leaf_id=leaf_id,
            root_area_id=root_area_id,
            message_ids=["msg"],
            created_at=now,
            status="failed",
            retry_count=3,  # At max
        )
        await db.LeafExtractionQueueManager.create(task_id, task)

        # Requeue with max_retries=3
        await db.LeafExtractionQueueManager.requeue_failed(max_retries=3)

        result = await db.LeafExtractionQueueManager.get_by_id(task_id)
        assert result.status == "failed"  # Still failed
