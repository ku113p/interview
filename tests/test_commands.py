"""Unit tests for command handlers."""

import secrets
import time
import uuid

from langchain_core.messages import AIMessage
from src.domain import InputMode, User
from src.infrastructure.db import managers as db
from src.infrastructure.db.api_managers import hash_key
from src.shared.ids import new_id
from src.workflows.nodes.commands import handlers
from src.workflows.nodes.commands.handle_command import handle_command
from src.workflows.nodes.commands.handlers import (
    HELP_TEXT,
    MIN_KEY_PREFIX,
    _delete_tokens,
    _reset_area_token_lookup,
    _reset_area_tokens,
    handle_clear,
    handle_delete_confirm,
    handle_delete_init,
    handle_help,
    handle_keys_command,
    handle_mode_set,
    handle_mode_show,
    handle_reset_area_confirm,
    handle_reset_area_init,
    process_command,
)
from src.workflows.routers.command_router import route_on_command


def _make_mock_state(user: User, text: str, command_response: str | None = None):
    """Create a mock state object with required fields for command testing."""

    class MockState:
        def __init__(self, user, text, command_response):
            self.user = user
            self.text = text
            self.command_response = command_response

    return MockState(user, text, command_response)


class TestHandleHelp:
    """Tests for /help command."""

    async def test_returns_help_text(self):
        """Help handler should return the help text."""
        result = await handle_help()
        assert result == HELP_TEXT

    async def test_help_text_contains_commands(self):
        """Help text should list available commands."""
        result = await handle_help()
        assert "/help" in result
        assert "/clear" in result
        assert "/delete" in result
        assert "/mode" in result


class TestHandleClear:
    """Tests for /clear command."""

    async def test_clear_no_history(self, temp_db, sample_user):
        """Clear with no history should return appropriate message."""
        result = await handle_clear(sample_user.id)
        assert "No conversation history" in result

    async def test_clear_with_history(self, temp_db, sample_user):
        """Clear should delete all histories and return count."""
        # Arrange - create histories
        for i in range(3):
            history = db.History(
                id=new_id(),
                message_data={"role": "user", "content": f"message {i}"},
                user_id=sample_user.id,
                created_ts=time.time(),
            )
            await db.HistoriesManager.create(history.id, history)

        # Act
        result = await handle_clear(sample_user.id)

        # Assert
        assert "Cleared 3 conversation" in result
        remaining = await db.HistoriesManager.list_by_user(sample_user.id)
        assert len(remaining) == 0


class TestHandleDeleteInit:
    """Tests for /delete command initialization."""

    async def test_generates_token(self, sample_user):
        """Delete init should generate and store a token."""
        # Clear any existing tokens
        _delete_tokens.clear()

        result = await handle_delete_init(sample_user.id)

        assert "WARNING" in result
        assert "permanently delete" in result
        assert "/delete_" in result
        assert sample_user.id in _delete_tokens

    async def test_token_in_response(self, sample_user):
        """Token in response should match stored token."""
        _delete_tokens.clear()

        result = await handle_delete_init(sample_user.id)

        stored_token, _ = _delete_tokens[sample_user.id]
        assert f"/delete_{stored_token}" in result

    async def test_token_expires_message(self, sample_user):
        """Response should mention token expiration."""
        _delete_tokens.clear()

        result = await handle_delete_init(sample_user.id)

        assert "60 seconds" in result


class TestHandleDeleteConfirm:
    """Tests for /delete_<token> confirmation."""

    async def test_no_pending_deletion(self, sample_user):
        """Confirm without init should fail."""
        _delete_tokens.clear()

        result = await handle_delete_confirm(sample_user.id, "anytoken")

        assert "No pending deletion" in result

    async def test_wrong_token(self, sample_user):
        """Confirm with wrong token should fail."""
        _delete_tokens.clear()
        _delete_tokens[sample_user.id] = ("correct_token", time.time())

        result = await handle_delete_confirm(sample_user.id, "wrong_token")

        assert "Invalid token" in result

    async def test_expired_token(self, sample_user):
        """Expired token should be rejected."""
        _delete_tokens.clear()
        # Set token with old timestamp
        old_time = time.time() - handlers.DELETE_TOKEN_TTL - 1
        _delete_tokens[sample_user.id] = ("old_token", old_time)

        result = await handle_delete_confirm(sample_user.id, "old_token")

        assert "No pending deletion" in result

    async def test_successful_deletion(self, temp_db, sample_user):
        """Successful deletion should remove all user data."""
        # Arrange - create user and data
        await db.UsersManager.create(
            sample_user.id,
            db.User(
                id=sample_user.id,
                name="test",
                mode=sample_user.mode.value,
                current_area_id=None,
            ),
        )

        # Create some history
        history = db.History(
            id=new_id(),
            message_data={"role": "user", "content": "test"},
            user_id=sample_user.id,
            created_ts=time.time(),
        )
        await db.HistoriesManager.create(history.id, history)

        # Set up valid token
        _delete_tokens.clear()
        token = "valid_token"
        _delete_tokens[sample_user.id] = (token, time.time())

        # Act
        result = await handle_delete_confirm(sample_user.id, token)

        # Assert
        assert "deleted" in result.lower()
        assert await db.UsersManager.get_by_id(sample_user.id) is None
        assert len(await db.HistoriesManager.list_by_user(sample_user.id)) == 0


class TestHandleModeShow:
    """Tests for /mode command (show current mode)."""

    async def test_shows_auto_mode(self):
        """Should show auto mode description."""
        user = User(id=new_id(), mode=InputMode.auto)

        result = await handle_mode_show(user)

        assert "auto" in result
        assert "Current mode" in result

    async def test_shows_interview_mode(self):
        """Should show interview mode description."""
        user = User(id=new_id(), mode=InputMode.conduct_interview)

        result = await handle_mode_show(user)

        assert "interview" in result

    async def test_shows_areas_mode(self):
        """Should show areas mode description."""
        user = User(id=new_id(), mode=InputMode.manage_areas)

        result = await handle_mode_show(user)

        assert "areas" in result


class TestHandleModeSet:
    """Tests for /mode <name> command."""

    async def test_set_auto_mode(self, temp_db, sample_user):
        """Should set mode to auto."""
        # Arrange
        await db.UsersManager.create(
            sample_user.id,
            db.User(
                id=sample_user.id,
                name="test",
                mode=InputMode.conduct_interview.value,
                current_area_id=None,
            ),
        )

        # Act
        result = await handle_mode_set(sample_user, "auto")

        # Assert
        assert "auto" in result
        db_user = await db.UsersManager.get_by_id(sample_user.id)
        assert db_user.mode == InputMode.auto.value

    async def test_set_interview_mode(self, temp_db, sample_user):
        """Should set mode to interview."""
        await db.UsersManager.create(
            sample_user.id,
            db.User(
                id=sample_user.id,
                name="test",
                mode=InputMode.auto.value,
                current_area_id=None,
            ),
        )

        result = await handle_mode_set(sample_user, "interview")

        assert "interview" in result
        db_user = await db.UsersManager.get_by_id(sample_user.id)
        assert db_user.mode == InputMode.conduct_interview.value

    async def test_set_areas_mode(self, temp_db, sample_user):
        """Should set mode to areas."""
        await db.UsersManager.create(
            sample_user.id,
            db.User(
                id=sample_user.id,
                name="test",
                mode=InputMode.auto.value,
                current_area_id=None,
            ),
        )

        result = await handle_mode_set(sample_user, "areas")

        assert "areas" in result
        db_user = await db.UsersManager.get_by_id(sample_user.id)
        assert db_user.mode == InputMode.manage_areas.value

    async def test_invalid_mode(self, temp_db, sample_user):
        """Should reject invalid mode names."""
        await db.UsersManager.create(
            sample_user.id,
            db.User(
                id=sample_user.id,
                name="test",
                mode=InputMode.auto.value,
                current_area_id=None,
            ),
        )

        result = await handle_mode_set(sample_user, "invalid")

        assert "Unknown mode" in result
        assert "auto" in result  # Should list valid modes

    async def test_case_insensitive(self, temp_db, sample_user):
        """Mode names should be case insensitive."""
        await db.UsersManager.create(
            sample_user.id,
            db.User(
                id=sample_user.id,
                name="test",
                mode=InputMode.auto.value,
                current_area_id=None,
            ),
        )

        result = await handle_mode_set(sample_user, "INTERVIEW")

        assert "interview" in result.lower()


class TestProcessCommand:
    """Tests for the main command dispatcher."""

    async def test_non_command_returns_none(self, sample_user):
        """Regular text should return None."""
        result = await process_command("hello world", sample_user)
        assert result is None

    async def test_help_command(self, sample_user):
        """Should dispatch /help."""
        result = await process_command("/help", sample_user)
        assert result == HELP_TEXT

    async def test_help_case_insensitive(self, sample_user):
        """Commands should be case insensitive."""
        result = await process_command("/HELP", sample_user)
        assert result == HELP_TEXT

    async def test_mode_without_arg(self, sample_user):
        """Should show mode when no argument."""
        result = await process_command("/mode", sample_user)
        assert "Current mode" in result

    async def test_mode_with_arg(self, temp_db, sample_user):
        """Should set mode when argument provided."""
        await db.UsersManager.create(
            sample_user.id,
            db.User(
                id=sample_user.id,
                name="test",
                mode=InputMode.auto.value,
                current_area_id=None,
            ),
        )

        result = await process_command("/mode interview", sample_user)
        assert "interview" in result

    async def test_unknown_command_returns_none(self, sample_user):
        """Unknown commands should return None."""
        result = await process_command("/unknown", sample_user)
        assert result is None

    async def test_delete_init(self, sample_user):
        """Should dispatch /delete."""
        _delete_tokens.clear()
        result = await process_command("/delete", sample_user)
        assert "WARNING" in result

    async def test_delete_with_token(self, sample_user):
        """Should dispatch /delete_<token>."""
        _delete_tokens.clear()
        result = await process_command("/delete_sometoken", sample_user)
        assert "No pending deletion" in result


class TestDeleteUserDataCascade:
    """Tests for cascading user data deletion."""

    async def test_deletes_all_user_data(self, temp_db, sample_user):
        """Deletion should remove all related data including API keys."""
        # Arrange - create user
        await db.UsersManager.create(
            sample_user.id,
            db.User(
                id=sample_user.id,
                name="test",
                mode=sample_user.mode.value,
                current_area_id=None,
            ),
        )

        # Create life area
        area_id = new_id()
        await db.LifeAreasManager.create(
            area_id,
            db.LifeArea(
                id=area_id,
                title="Test Area",
                parent_id=None,
                user_id=sample_user.id,
            ),
        )

        # Create history and link to leaf
        history_id = new_id()
        await db.HistoriesManager.create(
            history_id,
            db.History(
                id=history_id,
                message_data={"role": "user", "content": "test"},
                user_id=sample_user.id,
                created_ts=time.time(),
            ),
        )
        await db.LeafHistoryManager.link(area_id, history_id)

        # Create an API key
        raw_key = secrets.token_hex(32)
        api_key = db.ApiKey(
            id=new_id(),
            key_hash=hash_key(raw_key),
            key_prefix=raw_key[:8],
            user_id=sample_user.id,
            label="test-key",
            created_at=time.time(),
        )
        await db.ApiKeysManager.create(api_key.id, api_key)

        # Set up valid token and confirm deletion
        _delete_tokens.clear()
        token = "delete_token"
        _delete_tokens[sample_user.id] = (token, time.time())

        # Act
        await handle_delete_confirm(sample_user.id, token)

        # Assert - all data should be deleted
        assert await db.UsersManager.get_by_id(sample_user.id) is None
        assert len(await db.LifeAreasManager.list_by_user(sample_user.id)) == 0
        assert len(await db.HistoriesManager.list_by_user(sample_user.id)) == 0
        assert len(await db.ApiKeysManager.list_by_user(sample_user.id)) == 0


class TestHandleCommandNode:
    """Tests for the handle_command graph node."""

    async def test_returns_none_for_regular_text(self, sample_user):
        """Non-command text should return command_response=None."""
        state = _make_mock_state(sample_user, "hello world")

        result = await handle_command(state)

        assert result["command_response"] is None
        assert "messages" not in result

    async def test_returns_response_for_valid_command(self, sample_user):
        """Valid command should return response and add to messages."""
        state = _make_mock_state(sample_user, "/help")

        result = await handle_command(state)

        assert result["command_response"] == HELP_TEXT
        assert "messages" in result
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert result["messages"][0].content == HELP_TEXT

    async def test_returns_none_for_unknown_command(self, sample_user):
        """Unknown command should return command_response=None."""
        state = _make_mock_state(sample_user, "/unknowncommand")

        result = await handle_command(state)

        assert result["command_response"] is None
        assert "messages" not in result

    async def test_strips_whitespace(self, sample_user):
        """Command should work with leading/trailing whitespace."""
        state = _make_mock_state(sample_user, "  /help  ")

        result = await handle_command(state)

        assert result["command_response"] == HELP_TEXT


class TestRouteOnCommand:
    """Tests for the command router."""

    def test_routes_to_end_when_command_handled(self, sample_user):
        """Should route to END when command_response is set."""
        state = _make_mock_state(sample_user, "/help", command_response="Help text")

        result = route_on_command(state)

        assert result == "__end__"

    def test_routes_to_load_history_when_no_command(self, sample_user):
        """Should route to load_history when command_response is None."""
        state = _make_mock_state(sample_user, "hello", command_response=None)

        result = route_on_command(state)

        assert result == "load_history"

    def test_routes_to_load_history_for_unknown_command(self, sample_user):
        """Unknown commands should continue to load_history."""
        state = _make_mock_state(sample_user, "/unknown", command_response=None)

        result = route_on_command(state)

        assert result == "load_history"


class TestDeleteTokenIsolation:
    """Tests for multi-user token isolation."""

    async def test_user_cannot_use_another_users_token(self):
        """User A should not be able to confirm User B's deletion."""
        _delete_tokens.clear()

        user_a = User(id=uuid.uuid4(), mode=InputMode.auto)
        user_b = User(id=uuid.uuid4(), mode=InputMode.auto)

        # User A initiates deletion
        await handle_delete_init(user_a.id)
        token_a, _ = _delete_tokens[user_a.id]

        # User B tries to use User A's token
        result = await handle_delete_confirm(user_b.id, token_a)

        assert "No pending deletion" in result
        # User A's token should still be valid
        assert user_a.id in _delete_tokens

    async def test_tokens_are_user_specific(self):
        """Each user should have their own independent token."""
        _delete_tokens.clear()

        user_a = User(id=uuid.uuid4(), mode=InputMode.auto)
        user_b = User(id=uuid.uuid4(), mode=InputMode.auto)

        # Both users initiate deletion
        await handle_delete_init(user_a.id)
        await handle_delete_init(user_b.id)

        token_a, _ = _delete_tokens[user_a.id]
        token_b, _ = _delete_tokens[user_b.id]

        # Tokens should be different
        assert token_a != token_b
        assert user_a.id in _delete_tokens
        assert user_b.id in _delete_tokens


class TestHandleResetAreaInit:
    """Tests for /reset-area_<id> command initialization."""

    async def test_invalid_area_id(self, sample_user):
        """Invalid UUID should return error."""
        result = await handle_reset_area_init(sample_user.id, "not-a-uuid")
        assert "Invalid area ID" in result

    async def test_area_not_found(self, temp_db, sample_user):
        """Non-existent area should return error."""
        result = await handle_reset_area_init(sample_user.id, str(new_id()))
        assert "Area not found" in result

    async def test_wrong_user(self, temp_db, sample_user):
        """User cannot reset another user's area."""
        # Create area for different user
        other_user_id = new_id()
        area_id = new_id()
        await db.LifeAreasManager.create(
            area_id,
            db.LifeArea(
                id=area_id,
                title="Other's Area",
                parent_id=None,
                user_id=other_user_id,
            ),
        )

        result = await handle_reset_area_init(sample_user.id, str(area_id))
        assert "permission" in result.lower()

    async def test_generates_token(self, temp_db, sample_user):
        """Reset init should generate and store a token."""
        _reset_area_tokens.clear()
        _reset_area_token_lookup.clear()

        area_id = new_id()
        await db.LifeAreasManager.create(
            area_id,
            db.LifeArea(
                id=area_id,
                title="My Area",
                parent_id=None,
                user_id=sample_user.id,
            ),
        )

        result = await handle_reset_area_init(sample_user.id, str(area_id))

        assert "delete extracted knowledge" in result.lower()
        assert "/reset_area_" in result
        assert "60 seconds" in result
        assert (sample_user.id, area_id) in _reset_area_tokens


class TestHandleResetAreaConfirm:
    """Tests for /reset-area_<token> confirmation."""

    async def test_invalid_token(self, sample_user):
        """Invalid token should fail."""
        _reset_area_tokens.clear()
        _reset_area_token_lookup.clear()

        result = await handle_reset_area_confirm(sample_user.id, "badtoken")

        assert "Invalid or expired" in result

    async def test_expired_token(self, temp_db, sample_user):
        """Expired token should be rejected."""
        _reset_area_tokens.clear()
        _reset_area_token_lookup.clear()

        area_id = new_id()
        old_time = time.time() - handlers.RESET_TOKEN_TTL - 1
        _reset_area_tokens[(sample_user.id, area_id)] = ("old_token", old_time)

        result = await handle_reset_area_confirm(sample_user.id, "old_token")

        assert "Invalid or expired" in result

    async def test_successful_reset(self, temp_db, sample_user):
        """Successful reset should clear extraction data."""
        _reset_area_tokens.clear()
        _reset_area_token_lookup.clear()
        now = time.time()

        # Create area with history data
        area_id, history_id = new_id(), new_id()
        await db.LifeAreasManager.create(
            area_id,
            db.LifeArea(
                id=area_id,
                title="My Area",
                parent_id=None,
                user_id=sample_user.id,
            ),
        )
        # Create history and link to leaf
        await db.HistoriesManager.create(
            history_id,
            db.History(
                id=history_id,
                message_data={"role": "user", "content": "test"},
                user_id=sample_user.id,
                created_ts=now,
            ),
        )
        await db.LeafHistoryManager.link(area_id, history_id)

        # Set up valid token (both forward and reverse lookups)
        token = "valid_token"
        _reset_area_tokens[(sample_user.id, area_id)] = (token, now)
        _reset_area_token_lookup[(sample_user.id, token)] = area_id

        result = await handle_reset_area_confirm(sample_user.id, token)

        assert "Reset complete" in result and "My Area" in result

        # History should be cleared
        messages = await db.LeafHistoryManager.get_messages(area_id)
        assert len(messages) == 0


class TestProcessCommandResetArea:
    """Tests for reset-area dispatch in process_command."""

    async def test_reset_area_with_uuid(self, temp_db, sample_user):
        """Should dispatch /reset-area_<uuid> to init."""
        area_id = new_id()
        await db.LifeAreasManager.create(
            area_id,
            db.LifeArea(
                id=area_id,
                title="Area",
                parent_id=None,
                user_id=sample_user.id,
            ),
        )

        result = await process_command(f"/reset_area_{area_id}", sample_user)

        assert "delete extracted knowledge" in result.lower()

    async def test_reset_area_with_token(self, sample_user):
        """Should dispatch /reset-area_<token> to confirm."""
        _reset_area_tokens.clear()
        _reset_area_token_lookup.clear()

        result = await process_command("/reset_area_abc123", sample_user)

        assert "Invalid or expired" in result


class TestProcessCommandResetAreaCurrent:
    """Tests for /reset_area (no ID — resets current area)."""

    async def test_no_current_area(self, sample_user):
        """Should return helpful message when no current area is set."""
        result = await process_command("/reset_area", sample_user)
        assert result is not None
        assert "No current area set" in result

    async def test_with_current_area(self, temp_db, sample_user):
        """Should initiate reset for the user's current area."""
        area_id = new_id()
        await db.LifeAreasManager.create(
            area_id,
            db.LifeArea(
                id=area_id, title="Work", parent_id=None, user_id=sample_user.id
            ),
        )
        user_with_area = User(
            id=sample_user.id,
            mode=sample_user.mode,
            current_life_area_id=area_id,
        )
        result = await process_command("/reset_area", user_with_area)
        assert result is not None
        assert "delete extracted knowledge" in result.lower()
        assert "Work" in result


class TestResetAreaTokenIsolation:
    """Tests for multi-user reset-area token isolation."""

    async def test_user_cannot_use_another_users_token(self, temp_db):
        """User A should not be able to use User B's reset token."""
        _reset_area_tokens.clear()
        _reset_area_token_lookup.clear()

        user_a = User(id=uuid.uuid4(), mode=InputMode.auto)
        user_b = User(id=uuid.uuid4(), mode=InputMode.auto)

        # Create area for user A
        area_id = new_id()
        await db.LifeAreasManager.create(
            area_id,
            db.LifeArea(
                id=area_id,
                title="A's Area",
                parent_id=None,
                user_id=user_a.id,
            ),
        )

        # User A initiates reset
        await handle_reset_area_init(user_a.id, str(area_id))
        token_a, _ = _reset_area_tokens[(user_a.id, area_id)]

        # User B tries to use User A's token
        result = await handle_reset_area_confirm(user_b.id, token_a)

        assert "Invalid or expired" in result
        # Token should still be valid for user A
        assert (user_a.id, area_id) in _reset_area_tokens


class TestMcpKeysCommand:
    """Tests for /mcp_keys subcommands."""

    async def test_keys_list_empty(self, temp_db, sample_user):
        """List with no keys should show help message."""
        result = await handle_keys_command(sample_user.id, None)
        assert "No API keys" in result

    async def test_keys_create_and_list(self, temp_db, sample_user):
        """Create a key then list should show the key prefix."""
        result = await handle_keys_command(sample_user.id, "create my-tool")
        assert "Created API key" in result
        assert "my-tool" in result

        listing = await handle_keys_command(sample_user.id, None)
        assert "my-tool" in listing

    async def test_keys_revoke(self, temp_db, sample_user):
        """Revoke by prefix should delete the key."""
        create_result = await handle_keys_command(sample_user.id, "create to-revoke")
        # Extract raw key from create result (second line)
        raw_key = create_result.split("\n")[1]

        revoke_result = await handle_keys_command(
            sample_user.id, f"revoke {raw_key[:MIN_KEY_PREFIX]}"
        )
        assert "Revoked key" in revoke_result

        listing = await handle_keys_command(sample_user.id, None)
        assert "No API keys" in listing

    async def test_keys_revoke_prefix_too_short(self, temp_db, sample_user):
        """Revoke with too-short prefix should fail."""
        result = await handle_keys_command(sample_user.id, "revoke abc")
        assert "at least 8 characters" in result

    async def test_keys_revoke_not_found(self, temp_db, sample_user):
        """Revoke with non-matching prefix should report not found."""
        result = await handle_keys_command(sample_user.id, "revoke abcdef1234")
        assert "No key matching" in result

    async def test_keys_create_whitespace_label(self, temp_db, sample_user):
        """Whitespace-only label should not create a key."""
        result = await handle_keys_command(sample_user.id, "create    ")
        assert "Usage" in result

        listing = await handle_keys_command(sample_user.id, None)
        assert "No API keys" in listing

    async def test_keys_create_long_label_truncated(self, temp_db, sample_user):
        """Label longer than 64 chars should be truncated in listing."""
        long_label = "a" * 100
        result = await handle_keys_command(sample_user.id, f"create {long_label}")
        assert "Created API key" in result

        listing = await handle_keys_command(sample_user.id, None)
        assert "a" * 64 in listing
        assert "a" * 65 not in listing

    async def test_keys_unknown_subcommand(self, temp_db, sample_user):
        """Unknown subcommand should show usage."""
        result = await handle_keys_command(sample_user.id, "foobar")
        assert "Unknown subcommand" in result
