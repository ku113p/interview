"""Unit tests for leaf interview nodes and save_history persistence."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from src.domain import InputMode, User
from src.infrastructure.db import managers as db
from src.shared.ids import new_id
from src.shared.interview_models import LeafEvaluation
from src.shared.timestamp import get_timestamp
from src.workflows.nodes.persistence.save_history import (
    SaveHistoryState,
    save_history,
)
from src.workflows.subgraphs.leaf_interview.nodes import (
    create_turn_summary,
    generate_leaf_response,
    load_interview_context,
    quick_evaluate,
    select_next_leaf,
    update_coverage_status,
)
from src.workflows.subgraphs.leaf_interview.state import LeafInterviewState


def _create_state(user: User, area_id: uuid.UUID, **kwargs) -> LeafInterviewState:
    """Helper to create test LeafInterviewState objects."""
    defaults = {
        "messages": [],
        "messages_to_save": {},
        "is_fully_covered": False,
        "active_leaf_id": None,
        "leaf_evaluation": None,
        "question_text": None,
        "completed_leaf_path": None,
        "turn_summary_text": None,
        "set_covered_at": False,
    }
    defaults.update(kwargs)
    return LeafInterviewState(
        user=user,
        area_id=area_id,
        **defaults,
    )


async def _setup_leaf_with_history(user_id, area_id, leaf_id) -> uuid.UUID:
    """Create area, leaf, and history records for tests.

    Returns the history_id of the assistant (question) message.
    """
    now = get_timestamp()
    area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
    await db.LifeAreasManager.create(area_id, area)
    leaf = db.LifeArea(id=leaf_id, title="Skills", parent_id=area_id, user_id=user_id)
    await db.LifeAreasManager.create(leaf_id, leaf)

    question_hist_id = new_id()
    for i, (hist_id, role, content) in enumerate(
        [
            (question_hist_id, "assistant", "What Python skills?"),
            (new_id(), "user", "I have 5 years Python experience."),
        ]
    ):
        hist = db.History(
            id=hist_id,
            message_data={"role": role, "content": content},
            user_id=user_id,
            created_ts=now + i,
        )
        await db.HistoriesManager.create(hist_id, hist)
        await db.LeafHistoryManager.link(leaf_id, hist_id)

    return question_hist_id


async def _setup_two_leaves(user_id, area_id, leaf1_covered=False):
    """Create area with two leaf children; optionally mark leaf1 as covered."""
    now = get_timestamp()
    area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
    await db.LifeAreasManager.create(area_id, area)

    leaf1_id, leaf2_id = new_id(), new_id()
    covered_at = now if leaf1_covered else None
    leaf1 = db.LifeArea(
        id=leaf1_id,
        title="Skills",
        parent_id=area_id,
        user_id=user_id,
        covered_at=covered_at,
    )
    await db.LifeAreasManager.create(leaf1_id, leaf1)
    leaf2 = db.LifeArea(id=leaf2_id, title="Goals", parent_id=area_id, user_id=user_id)
    await db.LifeAreasManager.create(leaf2_id, leaf2)
    return leaf1_id, leaf2_id


def _create_save_state(user: User, **kwargs) -> SaveHistoryState:
    """Helper to create SaveHistoryState for tests."""
    defaults = {
        "messages_to_save": {},
        "is_successful": True,
        "active_leaf_id": None,
        "completed_leaf_id": None,
        "question_text": None,
        "is_fully_covered": False,
        "turn_summary_text": None,
        "set_covered_at": False,
    }
    defaults.update(kwargs)
    return SaveHistoryState(user=user, **defaults)


class TestCreateTurnSummary:
    """Tests for create_turn_summary node."""

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_active_leaf(self):
        """Should return {} when active_leaf_id is None."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(
            user, new_id(), active_leaf_id=None, messages=[HumanMessage(content="hi")]
        )
        result = await create_turn_summary(state, MagicMock())
        assert result == {}

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_human_message(self, temp_db):
        """Should return {} when messages contains only AI messages."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        await _setup_leaf_with_history(user_id, area_id, leaf_id)
        state = _create_state(
            user,
            area_id,
            active_leaf_id=leaf_id,
            messages=[AIMessage(content="Question?")],
        )
        result = await create_turn_summary(state, MagicMock())
        assert result == {}

    @pytest.mark.asyncio
    async def test_returns_empty_when_off_topic(self, temp_db):
        """Should return {} when LLM returns empty string (off-topic)."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        await _setup_leaf_with_history(user_id, area_id, leaf_id)
        state = _create_state(
            user,
            area_id,
            active_leaf_id=leaf_id,
            messages=[HumanMessage(content="What time is it?")],
        )
        mock_response = MagicMock()
        mock_response.content = ""
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        result = await create_turn_summary(state, mock_llm)
        assert result == {}

    @pytest.mark.asyncio
    async def test_returns_summary_text_on_success(self, temp_db):
        """Should return turn_summary_text when LLM returns content."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        await _setup_leaf_with_history(user_id, area_id, leaf_id)
        state = _create_state(
            user,
            area_id,
            active_leaf_id=leaf_id,
            messages=[HumanMessage(content="I know Python.")],
        )
        mock_response = MagicMock()
        mock_response.content = "User knows Python well."
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        result = await create_turn_summary(state, mock_llm)
        assert result == {"turn_summary_text": "User knows Python well."}


class TestLoadInterviewContext:
    """Tests for load_interview_context node."""

    @pytest.mark.asyncio
    async def test_returns_all_leaves_done_when_no_sub_areas(self, temp_db):
        """Should set active_leaf_id=None when root has no children."""
        user_id, area_id = new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)

        area = db.LifeArea(id=area_id, title="Empty", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)

        state = _create_state(user, area_id)
        result = await load_interview_context(state)

        assert result["active_leaf_id"] is None

    @pytest.mark.asyncio
    async def test_finds_first_uncovered_leaf(self, temp_db):
        """Should set active_leaf_id to first uncovered leaf."""
        user_id, area_id = new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)

        area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)

        leaf_id = new_id()
        leaf = db.LifeArea(
            id=leaf_id, title="Skills", parent_id=area_id, user_id=user_id
        )
        await db.LifeAreasManager.create(leaf_id, leaf)

        state = _create_state(user, area_id)
        result = await load_interview_context(state)

        assert result["active_leaf_id"] == leaf_id

    @pytest.mark.asyncio
    async def test_skips_covered_leaf_and_returns_next(self, temp_db):
        """Should skip leaf1 (covered_at set) and return leaf2."""
        user_id, area_id = new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        leaf1_id, leaf2_id = await _setup_two_leaves(
            user_id, area_id, leaf1_covered=True
        )

        state = _create_state(user, area_id)
        result = await load_interview_context(state)

        assert result["active_leaf_id"] == leaf2_id

    @pytest.mark.asyncio
    async def test_all_leaves_done_when_all_covered(self, temp_db):
        """Should return active_leaf_id=None when all leaves have covered_at set."""
        user_id, area_id = new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        now = get_timestamp()

        area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)

        leaf_id = new_id()
        leaf = db.LifeArea(
            id=leaf_id,
            title="Skills",
            parent_id=area_id,
            user_id=user_id,
            covered_at=now,
        )
        await db.LifeAreasManager.create(leaf_id, leaf)

        state = _create_state(user, area_id)
        result = await load_interview_context(state)

        assert result["active_leaf_id"] is None


class TestQuickEvaluate:
    """Tests for quick_evaluate node."""

    @pytest.mark.asyncio
    async def test_returns_none_when_all_leaves_done(self):
        """Should return None evaluation when active_leaf_id is None."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(user, new_id(), active_leaf_id=None)

        mock_llm = MagicMock()
        result = await quick_evaluate(state, mock_llm)

        assert result["leaf_evaluation"] is None
        mock_llm.with_structured_output.assert_not_called()

    @pytest.mark.asyncio
    async def test_evaluates_using_summaries(self, temp_db):
        """Should call LLM with aggregated summaries."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)

        now = get_timestamp()
        area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)
        leaf = db.LifeArea(
            id=leaf_id, title="Skills", parent_id=area_id, user_id=user_id
        )
        await db.LifeAreasManager.create(leaf_id, leaf)
        await db.SummariesManager.create_summary(
            area_id=leaf_id,
            summary_text="User has 5 years Python experience.",
            created_at=now,
        )

        state = _create_state(
            user,
            area_id,
            active_leaf_id=leaf_id,
            turn_summary_text="User has 5 years Python experience.",
        )

        mock_evaluation = LeafEvaluation(status="complete", reason="Sufficient detail")
        mock_structured_llm = AsyncMock()
        mock_structured_llm.ainvoke.return_value = mock_evaluation
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured_llm

        result = await quick_evaluate(state, mock_llm)

        assert result["leaf_evaluation"].status == "complete"
        mock_structured_llm.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_partial_when_no_summaries(self, temp_db):
        """Should return partial when there are no summaries yet."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)

        area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)
        leaf = db.LifeArea(
            id=leaf_id, title="Skills", parent_id=area_id, user_id=user_id
        )
        await db.LifeAreasManager.create(leaf_id, leaf)

        state = _create_state(user, area_id, active_leaf_id=leaf_id)
        mock_llm = MagicMock()

        result = await quick_evaluate(state, mock_llm)

        assert result["leaf_evaluation"].status == "partial"
        mock_llm.with_structured_output.assert_not_called()


class TestUpdateCoverageStatus:
    """Tests for update_coverage_status node."""

    @pytest.mark.asyncio
    async def test_returns_empty_when_all_leaves_done(self):
        """Should return is_successful when active_leaf_id is None."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(user, new_id(), active_leaf_id=None)
        mock_llm = MagicMock()

        result = await update_coverage_status(state, mock_llm)

        assert result == {"is_successful": True}

    @pytest.mark.asyncio
    async def test_signals_set_covered_at_when_complete(self):
        """Should return set_covered_at=True when evaluation is complete."""
        user = User(id=new_id(), mode=InputMode.auto)
        leaf_id = new_id()
        state = _create_state(
            user,
            new_id(),
            active_leaf_id=leaf_id,
            leaf_evaluation=LeafEvaluation(status="complete", reason="All answered"),
        )
        mock_llm = MagicMock()

        result = await update_coverage_status(state, mock_llm)

        assert result["completed_leaf_id"] == leaf_id
        assert result["set_covered_at"] is True

    @pytest.mark.asyncio
    async def test_signals_set_covered_at_when_skipped(self):
        """Should return set_covered_at=True when evaluation is skipped."""
        user = User(id=new_id(), mode=InputMode.auto)
        leaf_id = new_id()
        state = _create_state(
            user,
            new_id(),
            active_leaf_id=leaf_id,
            leaf_evaluation=LeafEvaluation(status="skipped", reason="Declined"),
        )
        mock_llm = MagicMock()

        result = await update_coverage_status(state, mock_llm)

        assert result["completed_leaf_id"] == leaf_id
        assert result["set_covered_at"] is True

    @pytest.mark.asyncio
    async def test_returns_empty_when_partial(self):
        """Should return empty dict when evaluation is partial."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(
            user,
            new_id(),
            active_leaf_id=new_id(),
            leaf_evaluation=LeafEvaluation(status="partial", reason="Need more info"),
        )
        mock_llm = MagicMock()

        result = await update_coverage_status(state, mock_llm)

        assert result == {}

    @pytest.mark.asyncio
    async def test_does_not_write_to_db(self, temp_db):
        """DB should NOT be updated by update_coverage_status (deferred to save_history)."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)

        area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)
        leaf = db.LifeArea(
            id=leaf_id, title="Skills", parent_id=area_id, user_id=user_id
        )
        await db.LifeAreasManager.create(leaf_id, leaf)

        state = _create_state(
            user,
            area_id,
            active_leaf_id=leaf_id,
            leaf_evaluation=LeafEvaluation(status="complete", reason="Done"),
        )
        mock_llm = MagicMock()
        await update_coverage_status(state, mock_llm)

        # DB leaf should still have covered_at=None (write is deferred)
        unchanged = await db.LifeAreasManager.get_by_id(leaf_id)
        assert unchanged.covered_at is None


class TestSelectNextLeaf:
    """Tests for select_next_leaf node."""

    @pytest.mark.asyncio
    async def test_returns_empty_when_all_done(self):
        """Should return is_successful when active_leaf_id is None."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(user, new_id(), active_leaf_id=None)

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

        assert result["completed_leaf_path"] is None

    @pytest.mark.asyncio
    async def test_moves_to_next_uncovered_leaf(self, temp_db):
        """Should move to next uncovered leaf, skipping the just-completed one.

        leaf1 covered_at is still NULL in DB (deferred write) but is excluded
        via completed_leaf_id so the next leaf (leaf2) is selected.
        """
        user_id, area_id = new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        leaf1_id, leaf2_id = await _setup_two_leaves(
            user_id, area_id, leaf1_covered=False
        )

        state = _create_state(
            user,
            area_id,
            active_leaf_id=leaf1_id,
            completed_leaf_id=leaf1_id,
            leaf_evaluation=LeafEvaluation(status="complete", reason="Done"),
        )

        result = await select_next_leaf(state)

        assert result["active_leaf_id"] == leaf2_id
        assert result["completed_leaf_path"] == "Skills"

        # DB should NOT have been updated (deferred to save_history)
        leaf1 = await db.LifeAreasManager.get_by_id(leaf1_id)
        assert leaf1.covered_at is None


class TestGenerateLeafResponse:
    """Tests for generate_leaf_response node."""

    @pytest.mark.asyncio
    async def test_bails_out_on_prior_failure(self):
        """Should return empty dict when is_successful is False."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(user, new_id(), is_successful=False, active_leaf_id=None)
        mock_llm = MagicMock()

        result = await generate_leaf_response(state, mock_llm)

        assert result == {}
        mock_llm.ainvoke.assert_not_called()

    @pytest.mark.asyncio
    async def test_generates_completion_when_all_done(self):
        """Should generate completion message when all leaves done."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(user, new_id(), active_leaf_id=None)

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

        area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)
        leaf = db.LifeArea(
            id=leaf_id, title="Skills", parent_id=area_id, user_id=user_id
        )
        await db.LifeAreasManager.create(leaf_id, leaf)

        state = _create_state(
            user,
            area_id,
            active_leaf_id=leaf_id,
            leaf_evaluation=None,
        )

        mock_response = MagicMock()
        mock_response.content = "Tell me about your skills."
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await generate_leaf_response(state, mock_llm)

        assert "messages" in result
        assert result["messages"][0].content == "Tell me about your skills."
        assert result["is_successful"] is True


class TestSaveHistoryLeafPersistence:
    """Tests for deferred leaf persistence in save_history."""

    @pytest.mark.asyncio
    async def test_sets_covered_at_on_completion(self, temp_db):
        """Should set covered_at on completed leaf."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        await _setup_leaf_with_history(user_id, area_id, leaf_id)

        ts = get_timestamp()
        state = _create_save_state(
            user,
            messages_to_save={ts: [AIMessage(content="Next question")]},
            active_leaf_id=leaf_id,
            completed_leaf_id=leaf_id,
            set_covered_at=True,
        )
        await save_history(state)

        updated = await db.LifeAreasManager.get_by_id(leaf_id)
        assert updated.covered_at is not None

    @pytest.mark.asyncio
    async def test_saves_turn_summary(self, temp_db):
        """Should save turn summary and return pending_summary_id."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        question_hist_id = await _setup_leaf_with_history(user_id, area_id, leaf_id)

        ts = get_timestamp()
        state = _create_save_state(
            user,
            messages_to_save={ts: [HumanMessage(content="My answer")]},
            active_leaf_id=leaf_id,
            turn_summary_text="User has Python skills.",
        )
        result = await save_history(state)

        summaries = await db.SummariesManager.list_by_area(leaf_id)
        assert len(summaries) == 1
        assert summaries[0].summary_text == "User has Python skills."
        assert summaries[0].vector is None  # Vector deferred to extraction

        # question_id must point to the question asked before this turn, not any
        # new AI message that may have been inserted in the same transaction
        assert summaries[0].question_id == question_hist_id

        # save_history should return pending_summary_id
        assert "pending_summary_id" in result
        assert result["pending_summary_id"] == summaries[0].id

    @pytest.mark.asyncio
    async def test_question_id_not_off_by_one_when_ai_message_in_same_save(
        self, temp_db
    ):
        """question_id must not point to the new AI message saved in the same call.

        Regression test: _resolve_question_id must run before _save_messages.
        If the new AI follow-up is inserted first, get_messages_with_ids would
        return it as the 'last AI message', giving the wrong question_id.
        """
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        question_hist_id = await _setup_leaf_with_history(user_id, area_id, leaf_id)

        ts = get_timestamp()
        # Both the user answer AND the AI follow-up are saved in one call —
        # the follow-up must NOT become the question_id.
        state = _create_save_state(
            user,
            messages_to_save={
                ts: [
                    HumanMessage(content="I know Python well."),
                    AIMessage(content="Tell me more about your projects."),
                ]
            },
            active_leaf_id=leaf_id,
            turn_summary_text="User knows Python well.",
        )
        await save_history(state)

        summaries = await db.SummariesManager.list_by_area(leaf_id)
        assert len(summaries) == 1
        assert summaries[0].question_id == question_hist_id

    @pytest.mark.asyncio
    async def test_saves_summary_and_covered_at_together(self, temp_db):
        """Should save summary and set covered_at atomically on completion."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        await _setup_leaf_with_history(user_id, area_id, leaf_id)

        ts = get_timestamp()
        state = _create_save_state(
            user,
            messages_to_save={ts: [AIMessage(content="Next question")]},
            completed_leaf_id=leaf_id,
            set_covered_at=True,
            turn_summary_text="User discussed their career goals.",
        )
        await save_history(state)

        updated = await db.LifeAreasManager.get_by_id(leaf_id)
        assert updated.covered_at is not None

        summaries = await db.SummariesManager.list_by_area(leaf_id)
        assert len(summaries) == 1
        assert summaries[0].summary_text == "User discussed their career goals."

    @pytest.mark.asyncio
    async def test_no_leaf_writes_without_completion(self, temp_db):
        """Should skip leaf writes when no completion data is present."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        await _setup_leaf_with_history(user_id, area_id, leaf_id)

        ts = get_timestamp()
        state = _create_save_state(
            user,
            messages_to_save={ts: [HumanMessage(content="My answer")]},
            active_leaf_id=leaf_id,
        )
        await save_history(state)

        # covered_at should remain None
        unchanged = await db.LifeAreasManager.get_by_id(leaf_id)
        assert unchanged.covered_at is None

    @pytest.mark.asyncio
    async def test_skips_covered_at_when_flag_false(self, temp_db):
        """Should skip setting covered_at when set_covered_at=False."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        await _setup_leaf_with_history(user_id, area_id, leaf_id)

        ts = get_timestamp()
        state = _create_save_state(
            user,
            messages_to_save={ts: [AIMessage(content="Next")]},
            completed_leaf_id=leaf_id,
            set_covered_at=False,  # explicitly False
        )
        await save_history(state)

        unchanged = await db.LifeAreasManager.get_by_id(leaf_id)
        assert unchanged.covered_at is None

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_failure(self, temp_db):
        """Should roll back all writes if an inner save step raises."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        await _setup_leaf_with_history(user_id, area_id, leaf_id)

        ts = get_timestamp()
        state = _create_save_state(
            user,
            messages_to_save={ts: [AIMessage(content="Next question")]},
            active_leaf_id=leaf_id,
            completed_leaf_id=leaf_id,
            set_covered_at=True,
            turn_summary_text="summary",
        )

        original_histories = await db.LeafHistoryManager.get_messages(leaf_id)
        original_count = len(original_histories)

        with MagicMock() as mock_covered:
            mock_covered.side_effect = RuntimeError("simulated failure")
            import unittest.mock as mock_module

            with mock_module.patch(
                "src.workflows.nodes.persistence.save_history._save_leaf_completion",
                side_effect=RuntimeError("simulated failure"),
            ):
                with pytest.raises(RuntimeError, match="simulated failure"):
                    await save_history(state)

        # Rollback: covered_at should still be None
        unchanged = await db.LifeAreasManager.get_by_id(leaf_id)
        assert unchanged.covered_at is None

        # Rollback: no new history records created
        histories = await db.LeafHistoryManager.get_messages(leaf_id)
        assert len(histories) == original_count
