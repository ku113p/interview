"""Unit tests for leaf interview nodes."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from src.domain import ClientMessage, InputMode, User
from src.infrastructure.db import managers as db
from src.processes.interview import State, Target
from src.shared.ids import new_id
from src.shared.interview_models import LeafEvaluation
from src.workflows.nodes.processing.leaf_interview import (
    generate_leaf_response,
    load_interview_context,
    quick_evaluate,
    select_next_leaf,
    update_coverage_status,
)


def _create_state(user: User, area_id: uuid.UUID, **kwargs) -> State:
    """Helper to create test State objects.

    Args:
        user: User object.
        area_id: Area UUID.
        **kwargs: Optional State fields (messages, active_leaf_id, active_leaf_path,
                  accumulated_message_ids, leaf_evaluation, question_text,
                  all_leaves_done, completed_leaf_path).
    """
    defaults = {
        "messages": [],
        "messages_to_save": {},
        "is_fully_covered": False,
        "active_leaf_id": None,
        "active_leaf_path": None,
        "accumulated_message_ids": None,
        "leaf_evaluation": None,
        "question_text": None,
        "all_leaves_done": False,
        "completed_leaf_path": None,
    }
    defaults.update(kwargs)
    return State(
        user=user,
        message=ClientMessage(data="test"),
        text="test",
        target=Target.conduct_interview,
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
        assert result["active_leaf_path"] == "Skills"

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
            message_ids=["msg1", "msg2"],
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
        assert result["active_leaf_path"] == "Skills"
        assert result["accumulated_message_ids"] == ["msg1", "msg2"]
        assert result["question_text"] == "What are your skills?"


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
            active_leaf_path="Skills > Python",
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
        """Should return empty dict when all leaves are done."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(user, new_id(), all_leaves_done=True)

        result = await update_coverage_status(state)

        assert result == {}

    @pytest.mark.asyncio
    async def test_saves_user_message(self, temp_db):
        """Should save user message to database."""
        user_id, area_id, leaf_id = new_id(), new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)

        # Create area and leaf
        area = db.LifeArea(id=area_id, title="Career", parent_id=None, user_id=user_id)
        await db.LifeAreasManager.create(area_id, area)

        # Create active context
        from src.shared.timestamp import get_timestamp

        ctx = db.ActiveInterviewContext(
            user_id=user_id,
            root_area_id=area_id,
            active_leaf_id=leaf_id,
            created_at=get_timestamp(),
            message_ids=[],
        )
        await db.ActiveInterviewContextManager.create(user_id, ctx)

        state = _create_state(
            user,
            area_id,
            messages=[HumanMessage(content="I know Python")],
            active_leaf_id=leaf_id,
            accumulated_message_ids=[],
            leaf_evaluation=LeafEvaluation(status="partial", reason="Need more detail"),
        )

        result = await update_coverage_status(state)

        assert "accumulated_message_ids" in result
        assert len(result["accumulated_message_ids"]) == 1

        # Verify message was saved
        messages = await db.LifeAreaMessagesManager.list_by_area(area_id)
        assert len(messages) == 1
        assert "I know Python" in messages[0].message_text


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
        message_ids=[],
    )
    await db.ActiveInterviewContextManager.create(user_id, ctx)
    return leaf1_id, leaf2_id


class TestSelectNextLeaf:
    """Tests for select_next_leaf node."""

    @pytest.mark.asyncio
    async def test_returns_empty_when_all_done(self):
        """Should return empty dict when all leaves already done."""
        user = User(id=new_id(), mode=InputMode.auto)
        state = _create_state(user, new_id(), all_leaves_done=True)

        result = await select_next_leaf(state)

        assert result == {}

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
        """Should move to next uncovered leaf when current is complete."""
        user_id, area_id = new_id(), new_id()
        user = User(id=user_id, mode=InputMode.auto)
        leaf1_id, leaf2_id = await _setup_two_leaves_with_coverage(user_id, area_id)

        state = _create_state(
            user,
            area_id,
            active_leaf_id=leaf1_id,
            active_leaf_path="Skills",
            leaf_evaluation=LeafEvaluation(status="complete", reason="Done"),
        )

        result = await select_next_leaf(state)

        assert result["active_leaf_id"] == leaf2_id
        assert result["active_leaf_path"] == "Goals"
        assert result["completed_leaf_path"] == "Skills"


class TestGenerateLeafResponse:
    """Tests for generate_leaf_response node."""

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
            message_ids=[],
        )
        await db.ActiveInterviewContextManager.create(user_id, ctx)

        state = _create_state(
            user,
            area_id,
            active_leaf_id=leaf_id,
            active_leaf_path="Career > Skills",
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
