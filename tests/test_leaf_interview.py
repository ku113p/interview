"""Unit tests for leaf interview nodes and save_history persistence."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from src.domain import InputMode, User
from src.infrastructure.db import managers as db
from src.shared.ids import new_id
from src.shared.interview_models import LeafEvaluation
from src.workflows.nodes.persistence.save_history import (
    SaveHistoryState,
    save_history,
)
from src.workflows.subgraphs.leaf_interview.nodes import (
    generate_leaf_response,
    load_interview_context,
    quick_evaluate,
    select_next_leaf,
    update_coverage_status,
)
from src.workflows.subgraphs.leaf_interview.state import LeafInterviewState


def _create_state(user: User, area_id: uuid.UUID, **kwargs) -> LeafInterviewState:
    """Helper to create test LeafInterviewState objects.

    Args:
        user: User object.
        area_id: Area UUID.
        **kwargs: Optional State fields (messages, active_leaf_id,
                  leaf_evaluation, question_text, all_leaves_done, completed_leaf_path).
    """
    defaults = {
        "messages": [],
        "messages_to_save": {},
        "is_fully_covered": False,
        "active_leaf_id": None,
        "leaf_evaluation": None,
        "question_text": None,
        "all_leaves_done": False,
        "completed_leaf_path": None,
    }
    defaults.update(kwargs)
    return LeafInterviewState(
        user=user,
        area_id=area_id,
        **defaults,
    )


class TestLoadInterviewContext:
    """Tests for load_interview_context node."""

    @pytest.mark.asyncio
    async def test_returns_all_leaves_done_when_no_sub_areas(self, temp_db):
        """Should mark all_leaves_done when root has no children."""
        user_id, area_id = new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)

        # Create root area with no children
        area = db.LifeArea(id=area_id, title="Empty", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)

        state = _create_state(user, area_id)
        result = await load_interview_context(state)

        assert result["all_leaves_done"] is True
        assert result["active_leaf_id"] is None

    @pytest.mark.asyncio
    async def test_creates_coverage_records_for_leaves(self, temp_db):
        """Should create leaf_coverage records for leaf areas."""
        user_id, area_id = new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)

        # Create root with one leaf child
        area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)

        leaf_id = new_id()
        leaf = db.LifeArea(
            id=leaf_id, title="Skills", parent_id=area_id, user_id=user_id
        )
        await db.LifeAreasManager.create(leaf_id, leaf)

        state = _create_state(user, area_id)
        result = await load_interview_context(state)

        assert result["all_leaves_done"] is False
        assert result["active_leaf_id"] == leaf_id

        # Verify coverage record was created
        coverage = await db.LeafCoverageManager.list_by_root_area(area_id)
        assert len(coverage) == 1
        assert coverage[0].leaf_id == leaf_id
        assert coverage[0].status == "active"

    @pytest.mark.asyncio
    async def test_loads_existing_context(self, temp_db):
        """Should restore state from existing active context."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)

        # Create area structure
        area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)
        leaf = db.LifeArea(
            id=leaf_id, title="Skills", parent_id=area_id, user_id=user_id
        )
        await db.LifeAreasManager.create(leaf_id, leaf)

        # Create existing context
        from src.shared.timestamp import get_timestamp

        ctx = db.ActiveInterviewContext(
            user_id=user_id,
            root_area_id=area_id,
            active_leaf_id=leaf_id,
            created_at=get_timestamp(),
            question_text="What are your skills?",
        )
        await db.ActiveInterviewContextManager.create(user_id, ctx)

        # Create coverage record
        coverage = db.LeafCoverage(
            leaf_id=leaf_id,
            root_area_id=area_id,
            status="active",
            updated_at=get_timestamp(),
        )
        await db.LeafCoverageManager.create(leaf_id, coverage)

        state = _create_state(user, area_id)
        result = await load_interview_context(state)

        assert result["active_leaf_id"] == leaf_id
        assert result["question_text"] == "What are your skills?"

    @pytest.mark.asyncio
    async def test_returns_already_extracted_when_area_has_extracted_at(self, temp_db):
        """Should bail early when area already has extracted_at set."""
        from src.shared.timestamp import get_timestamp

        user_id, area_id = new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)

        area = db.LifeArea(
            id=area_id,
            title="Career",
            parent_id=None,
            user_id=user_id,
            extracted_at=get_timestamp(),
        )
        await db.LifeAreasManager.create(area_id, area)

        state = _create_state(user, area_id)
        result = await load_interview_context(state)

        assert result["area_already_extracted"] is True
        assert result["all_leaves_done"] is True
        assert result["active_leaf_id"] is None

    @pytest.mark.asyncio
    async def test_auto_advances_past_covered_leaf(self, temp_db):
        """Should advance to next uncovered leaf when context points to a covered one."""
        user_id, area_id = new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)

        leaf1_id, leaf2_id = await _setup_two_leaves_with_coverage(
            user_id, area_id, leaf1_status="covered"
        )

        state = _create_state(user, area_id)
        result = await load_interview_context(state)

        assert result["active_leaf_id"] == leaf2_id
        assert result["all_leaves_done"] is False


class TestQuickEvaluate:
    """Tests for quick_evaluate node."""

    @pytest.mark.asyncio
    async def test_returns_none_when_all_leaves_done(self):
        """Should return None evaluation when all leaves done."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(user, new_id(), all_leaves_done=True)

        mock_llm = MagicMock()
        result = await quick_evaluate(state, mock_llm)

        assert result["leaf_evaluation"] is None
        mock_llm.with_structured_output.assert_not_called()

    @pytest.mark.asyncio
    async def test_evaluates_user_response(self):
        """Should evaluate user's response using LLM."""
        user = User(id=new_id(), mode=InputMode.auto)
        leaf_id = new_id()
        state = _create_state(
            user,
            new_id(),
            messages=[HumanMessage(content="I have 5 years of Python experience")],
            active_leaf_id=leaf_id,
            question_text="What is your Python experience?",
        )

        mock_evaluation = LeafEvaluation(
            status="complete", reason="Provided specific details"
        )
        mock_structured_llm = AsyncMock()
        mock_structured_llm.ainvoke.return_value = mock_evaluation

        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured_llm

        result = await quick_evaluate(state, mock_llm)

        assert result["leaf_evaluation"].status == "complete"
        mock_structured_llm.ainvoke.assert_called_once()


class TestUpdateCoverageStatus:
    """Tests for update_coverage_status node."""

    @pytest.mark.asyncio
    async def test_returns_empty_when_all_leaves_done(self):
        """Should return is_successful when all leaves are done."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(user, new_id(), all_leaves_done=True)
        mock_llm = MagicMock()

        result = await update_coverage_status(state, mock_llm)

        assert result == {"is_successful": True}

    @pytest.mark.asyncio
    async def test_returns_completion_data_when_complete(self, temp_db):
        """Should return completion data in state without writing to DB."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)

        # Create area and leaf
        area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)

        from src.shared.timestamp import get_timestamp

        now = get_timestamp()
        coverage = db.LeafCoverage(
            leaf_id=leaf_id, root_area_id=area_id, status="active", updated_at=now
        )
        await db.LeafCoverageManager.create(leaf_id, coverage)

        state = _create_state(
            user,
            area_id,
            active_leaf_id=leaf_id,
            leaf_evaluation=LeafEvaluation(status="complete", reason="All answered"),
        )

        # Mock LLM for summary extraction
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "User discussed their career goals."
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await update_coverage_status(state, mock_llm)

        # Returns completion data in state for deferred persistence
        assert result["completed_leaf_id"] == leaf_id
        assert result["leaf_completion_status"] == "covered"

        # DB should NOT be updated yet (deferred to save_history)
        unchanged = await db.LeafCoverageManager.get_by_id(leaf_id)
        assert unchanged.status == "active"

    @pytest.mark.asyncio
    async def test_returns_summary_data_in_state(self, temp_db):
        """Should return summary text in state for deferred persistence."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        await _setup_leaf_with_history(user_id, area_id, leaf_id)

        state = _create_state(
            user,
            area_id,
            active_leaf_id=leaf_id,
            leaf_evaluation=LeafEvaluation(status="complete", reason="All answered"),
        )
        mock_llm = _mock_llm_for_summary()

        result = await update_coverage_status(state, mock_llm)

        assert result["completed_leaf_id"] == leaf_id
        assert result["leaf_completion_status"] == "covered"
        assert result["leaf_summary_text"] == "User has 5 years of Python experience."
        assert "leaf_summary_vector" not in result

        # DB should NOT be updated yet
        unchanged = await db.LeafCoverageManager.get_by_id(leaf_id)
        assert unchanged.status == "active"
        assert unchanged.summary_text is None

    @pytest.mark.asyncio
    async def test_extracts_summary_on_first_turn_without_db_history(self, temp_db):
        """Should extract summary from state.messages when DB history is empty."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)

        # Create area and coverage but NO history messages in DB
        area = db.LifeArea(id=area_id, title="Sports", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)

        from src.shared.timestamp import get_timestamp

        now = get_timestamp()
        coverage = db.LeafCoverage(
            leaf_id=leaf_id,
            root_area_id=area_id,
            status="active",
            updated_at=now,
        )
        await db.LeafCoverageManager.create(leaf_id, coverage)

        state = _create_state(
            user,
            area_id,
            active_leaf_id=leaf_id,
            messages=[HumanMessage(content="I play basketball and tennis")],
            leaf_evaluation=LeafEvaluation(status="complete", reason="All answered"),
        )
        mock_llm = _mock_llm_for_summary()

        result = await update_coverage_status(state, mock_llm)

        assert result["completed_leaf_id"] == leaf_id
        assert result["leaf_summary_text"] is not None
        mock_llm.ainvoke.assert_called_once()


def _mock_llm_for_summary():
    """Create mock LLM for summary extraction tests."""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "User has 5 years of Python experience."
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)
    return mock_llm


async def _setup_leaf_with_history(user_id, area_id, leaf_id):
    """Create area, leaf, coverage, and history records for summary tests."""
    from src.shared.timestamp import get_timestamp

    area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
    await db.LifeAreasManager.create(area_id, area)
    leaf = db.LifeArea(id=leaf_id, title="Skills", parent_id=area_id, user_id=user_id)
    await db.LifeAreasManager.create(leaf_id, leaf)

    now = get_timestamp()
    coverage = db.LeafCoverage(
        leaf_id=leaf_id, root_area_id=area_id, status="active", updated_at=now
    )
    await db.LeafCoverageManager.create(leaf_id, coverage)

    # Create and link history messages
    for i, (role, content) in enumerate(
        [
            ("assistant", "What Python skills?"),
            ("user", "I have 5 years Python experience."),
        ]
    ):
        hist_id = new_id()
        hist = db.History(
            id=hist_id,
            message_data={"role": role, "content": content},
            user_id=user_id,
            created_ts=now + i,
        )
        await db.HistoriesManager.create(hist_id, hist)
        await db.LeafHistoryManager.link(leaf_id, hist_id)


async def _setup_two_leaves_with_coverage(user_id, area_id, leaf1_status="covered"):
    """Create area with two leaves and coverage records for select_next_leaf tests."""
    from src.shared.timestamp import get_timestamp

    area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
    await db.LifeAreasManager.create(area_id, area)

    leaf1_id, leaf2_id = new_id(), new_id()
    for lid, title in [(leaf1_id, "Skills"), (leaf2_id, "Goals")]:
        leaf = db.LifeArea(id=lid, title=title, parent_id=area_id, user_id=user_id)
        await db.LifeAreasManager.create(lid, leaf)

    now = get_timestamp()
    for lid, status in [(leaf1_id, leaf1_status), (leaf2_id, "pending")]:
        cov = db.LeafCoverage(
            leaf_id=lid, root_area_id=area_id, status=status, updated_at=now
        )
        await db.LeafCoverageManager.create(lid, cov)

    ctx = db.ActiveInterviewContext(
        user_id=user_id,
        root_area_id=area_id,
        active_leaf_id=leaf1_id,
        created_at=now,
    )
    await db.ActiveInterviewContextManager.create(user_id, ctx)
    return leaf1_id, leaf2_id


class TestSelectNextLeaf:
    """Tests for select_next_leaf node."""

    @pytest.mark.asyncio
    async def test_returns_empty_when_all_done(self):
        """Should return is_successful when all leaves already done."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(user, new_id(), all_leaves_done=True)

        result = await select_next_leaf(state)

        assert result == {"is_successful": True}

    @pytest.mark.asyncio
    async def test_stays_on_current_when_partial(self):
        """Should stay on current leaf when evaluation is partial."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(
            user,
            new_id(),
            active_leaf_id=new_id(),
            leaf_evaluation=LeafEvaluation(status="partial", reason="Need more info"),
        )

        result = await select_next_leaf(state)

        assert result["all_leaves_done"] is False
        assert result["completed_leaf_path"] is None

    @pytest.mark.asyncio
    async def test_moves_to_next_uncovered_leaf(self, temp_db):
        """Should move to next uncovered leaf, excluding the just-completed one.

        leaf1 status remains 'active' in DB (deferred write) but is excluded
        via exclude_ids so the next uncovered leaf (leaf2) is selected.
        """
        user_id, area_id = new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        leaf1_id, leaf2_id = await _setup_two_leaves_with_coverage(
            user_id, area_id, leaf1_status="active"
        )

        state = _create_state(
            user,
            area_id,
            active_leaf_id=leaf1_id,
            leaf_evaluation=LeafEvaluation(status="complete", reason="Done"),
        )

        result = await select_next_leaf(state)

        assert result["active_leaf_id"] == leaf2_id
        assert result["completed_leaf_path"] == "Skills"

        # DB should NOT have been updated (deferred to save_history)
        ctx = await db.ActiveInterviewContextManager.get_by_user(user_id)
        assert ctx.active_leaf_id == leaf1_id  # Still points to old leaf


class TestGenerateLeafResponse:
    """Tests for generate_leaf_response node."""

    @pytest.mark.asyncio
    async def test_bails_out_on_prior_failure(self):
        """Should return empty dict when is_successful is False."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(user, new_id(), is_successful=False, all_leaves_done=True)
        mock_llm = MagicMock()

        result = await generate_leaf_response(state, mock_llm)

        assert result == {}
        mock_llm.ainvoke.assert_not_called()

    @pytest.mark.asyncio
    async def test_generates_completion_when_all_done(self):
        """Should generate completion message when all leaves done."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(user, new_id(), all_leaves_done=True)

        mock_response = MagicMock()
        mock_response.content = "Thank you for sharing! This area is complete."

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await generate_leaf_response(state, mock_llm)

        assert "messages" in result
        assert isinstance(result["messages"][0], AIMessage)
        assert result["is_successful"] is True

    @pytest.mark.asyncio
    async def test_generates_question_for_new_leaf(self, temp_db):
        """Should generate initial question for a new leaf."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)

        # Create context
        from src.shared.timestamp import get_timestamp

        ctx = db.ActiveInterviewContext(
            user_id=user_id,
            root_area_id=area_id,
            active_leaf_id=leaf_id,
            created_at=get_timestamp(),
        )
        await db.ActiveInterviewContextManager.create(user_id, ctx)

        state = _create_state(
            user,
            area_id,
            active_leaf_id=leaf_id,
            leaf_evaluation=None,  # No evaluation yet = initial question
        )

        mock_response = MagicMock()
        mock_response.content = "Tell me about your skills."

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await generate_leaf_response(state, mock_llm)

        assert "messages" in result
        assert result["messages"][0].content == "Tell me about your skills."
        assert result["is_successful"] is True


def _create_save_state(user: User, **kwargs) -> SaveHistoryState:
    """Helper to create SaveHistoryState for tests."""
    defaults = {
        "messages_to_save": {},
        "is_successful": True,
        "active_leaf_id": None,
        "completed_leaf_id": None,
        "question_text": None,
        "is_fully_covered": False,
        "leaf_summary_text": None,
        "leaf_completion_status": None,
    }
    defaults.update(kwargs)
    return SaveHistoryState(user=user, **defaults)


class TestSaveHistoryLeafPersistence:
    """Tests for deferred leaf persistence in save_history."""

    @pytest.mark.asyncio
    async def test_persists_leaf_completion_status(self, temp_db):
        """Should mark completed leaf as covered in DB."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        await _setup_leaf_with_history(user_id, area_id, leaf_id)

        from src.shared.timestamp import get_timestamp

        ts = get_timestamp()
        state = _create_save_state(
            user,
            messages_to_save={ts: [AIMessage(content="Next question")]},
            active_leaf_id=leaf_id,
            completed_leaf_id=leaf_id,
            leaf_completion_status="covered",
        )
        await save_history(state)

        updated = await db.LeafCoverageManager.get_by_id(leaf_id)
        assert updated.status == "covered"

    @pytest.mark.asyncio
    async def test_persists_leaf_summary_text(self, temp_db):
        """Should save summary text to DB (vector deferred to extraction)."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        await _setup_leaf_with_history(user_id, area_id, leaf_id)

        from src.shared.timestamp import get_timestamp

        ts = get_timestamp()
        state = _create_save_state(
            user,
            messages_to_save={ts: [AIMessage(content="Next question")]},
            completed_leaf_id=leaf_id,
            leaf_completion_status="covered",
            leaf_summary_text="User has Python skills",
        )
        await save_history(state)

        updated = await db.LeafCoverageManager.get_by_id(leaf_id)
        assert updated.summary_text == "User has Python skills"
        assert updated.vector is None  # Vector deferred to extraction process
        assert updated.status == "covered"

    @pytest.mark.asyncio
    async def test_persists_context_transition(self, temp_db):
        """Should update active leaf and mark new leaf active on transition."""
        user_id, area_id = new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        leaf1_id, leaf2_id = await _setup_two_leaves_with_coverage(
            user_id, area_id, leaf1_status="active"
        )

        from src.shared.timestamp import get_timestamp

        ts = get_timestamp()
        state = _create_save_state(
            user,
            messages_to_save={ts: [AIMessage(content="Next question")]},
            active_leaf_id=leaf2_id,
            completed_leaf_id=leaf1_id,
            leaf_completion_status="covered",
            question_text="Tell me about your goals",
        )
        await save_history(state)

        # Completed leaf should be marked covered
        leaf1 = await db.LeafCoverageManager.get_by_id(leaf1_id)
        assert leaf1.status == "covered"

        # New leaf should be marked active
        leaf2 = await db.LeafCoverageManager.get_by_id(leaf2_id)
        assert leaf2.status == "active"

        # Context should point to new leaf
        ctx = await db.ActiveInterviewContextManager.get_by_user(user_id)
        assert ctx.active_leaf_id == leaf2_id
        assert ctx.question_text == "Tell me about your goals"

    @pytest.mark.asyncio
    async def test_deletes_context_when_fully_covered(self, temp_db):
        """Should delete interview context when all leaves are covered."""
        user_id, area_id = new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        leaf1_id, _ = await _setup_two_leaves_with_coverage(
            user_id, area_id, leaf1_status="active"
        )

        from src.shared.timestamp import get_timestamp

        ts = get_timestamp()
        state = _create_save_state(
            user,
            messages_to_save={ts: [AIMessage(content="All done!")]},
            completed_leaf_id=leaf1_id,
            leaf_completion_status="covered",
            is_fully_covered=True,
        )
        await save_history(state)

        # Context should be deleted
        ctx = await db.ActiveInterviewContextManager.get_by_user(user_id)
        assert ctx is None

        # Completed leaf should still be marked covered
        leaf1 = await db.LeafCoverageManager.get_by_id(leaf1_id)
        assert leaf1.status == "covered"

    @pytest.mark.asyncio
    async def test_no_leaf_writes_without_completion(self, temp_db):
        """Should skip leaf writes when no completion data is present."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        await _setup_leaf_with_history(user_id, area_id, leaf_id)

        from src.shared.timestamp import get_timestamp

        ts = get_timestamp()
        state = _create_save_state(
            user,
            messages_to_save={ts: [HumanMessage(content="My answer")]},
            active_leaf_id=leaf_id,
        )
        await save_history(state)

        # Coverage should remain unchanged
        unchanged = await db.LeafCoverageManager.get_by_id(leaf_id)
        assert unchanged.status == "active"

    @pytest.mark.asyncio
    async def test_saves_summary_text_without_vector(self, temp_db):
        """Should save summary text even without vector (vector deferred to extraction)."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        await _setup_leaf_with_history(user_id, area_id, leaf_id)

        from src.shared.timestamp import get_timestamp

        ts = get_timestamp()
        state = _create_save_state(
            user,
            messages_to_save={ts: [AIMessage(content="Next")]},
            completed_leaf_id=leaf_id,
            leaf_completion_status="covered",
            leaf_summary_text="Some summary",
        )
        await save_history(state)

        # Summary text saved, vector remains None (deferred to extraction)
        updated = await db.LeafCoverageManager.get_by_id(leaf_id)
        assert updated.status == "covered"
        assert updated.summary_text == "Some summary"
        assert updated.vector is None

    @pytest.mark.asyncio
    async def test_skips_completion_when_status_missing(self, temp_db):
        """Should skip leaf writes when completed_leaf_id set but status is None."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        await _setup_leaf_with_history(user_id, area_id, leaf_id)

        from src.shared.timestamp import get_timestamp

        ts = get_timestamp()
        state = _create_save_state(
            user,
            messages_to_save={ts: [AIMessage(content="Next")]},
            completed_leaf_id=leaf_id,
            leaf_completion_status=None,  # Missing status
        )
        await save_history(state)

        # Coverage should remain unchanged
        unchanged = await db.LeafCoverageManager.get_by_id(leaf_id)
        assert unchanged.status == "active"

    @pytest.mark.asyncio
    async def test_transaction_rollback_leaves_no_partial_state(self, temp_db):
        """Should roll back all writes if _save_context_transition fails."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        await _setup_leaf_with_history(user_id, area_id, leaf_id)

        from src.shared.timestamp import get_timestamp

        ts = get_timestamp()
        state = _create_save_state(
            user,
            messages_to_save={ts: [AIMessage(content="Next question")]},
            active_leaf_id=leaf_id,
            completed_leaf_id=leaf_id,
            leaf_completion_status="covered",
            leaf_summary_text="summary",
        )

        with patch(
            "src.workflows.nodes.persistence.save_history._save_context_transition",
            side_effect=RuntimeError("simulated failure"),
        ):
            with pytest.raises(RuntimeError, match="simulated failure"):
                await save_history(state)

        # Rollback: coverage status should still be "active"
        unchanged = await db.LeafCoverageManager.get_by_id(leaf_id)
        assert unchanged.status == "active"
        assert unchanged.summary_text is None

        # Rollback: no new history records created
        histories = await db.LeafHistoryManager.get_messages(leaf_id)
        # Only the 2 original messages from _setup_leaf_with_history
        assert len(histories) == 2
