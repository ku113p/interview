"""Command handler implementations."""

import secrets
import time
import uuid
from typing import Callable, Coroutine

import aiosqlite

from src.domain import InputMode, User
from src.infrastructure.db import managers as db
from src.infrastructure.db.connection import transaction

HELP_TEXT = """Commands:
  /help      Show this help
  /clear     Clear conversation history
  /delete    Delete your account (requires confirmation)
  /mode      Show current input mode
  /mode <name>  Change mode (auto, interview, areas)
  /reset_area      Reset the current area (requires confirmation)
  /mcp_keys      List API keys for MCP server
  /mcp_keys create <label>  Create new API key
  /mcp_keys revoke <prefix>  Revoke API key
"""

# Module-level storage for delete tokens.
# NOTE: This only works within a single process. If workers run in separate
# processes (e.g., multiprocessing), tokens won't be shared across them.
# For multi-process deployments, consider using a database table or Redis.
_delete_tokens: dict[uuid.UUID, tuple[str, float]] = {}
DELETE_TOKEN_TTL = 60.0

# Storage for reset-area tokens: (user_id, area_id) -> (token, timestamp)
_reset_area_tokens: dict[tuple[uuid.UUID, uuid.UUID], tuple[str, float]] = {}
# Reverse lookup: (user_id, token) -> area_id for O(1) token validation
_reset_area_token_lookup: dict[tuple[uuid.UUID, str], uuid.UUID] = {}
RESET_TOKEN_TTL = 60.0
MIN_KEY_PREFIX = 8


def _cleanup_expired_tokens() -> None:
    """Remove expired delete tokens."""
    now = time.time()
    expired = [
        uid for uid, (_, ts) in _delete_tokens.items() if now - ts > DELETE_TOKEN_TTL
    ]
    for uid in expired:
        _delete_tokens.pop(uid, None)


def _cleanup_expired_reset_tokens() -> None:
    """Remove expired reset-area tokens."""
    now = time.time()
    expired = [
        key for key, (_, ts) in _reset_area_tokens.items() if now - ts > RESET_TOKEN_TTL
    ]
    for key in expired:
        token_data = _reset_area_tokens.pop(key, None)
        if token_data:
            user_id, area_id = key
            token, _ = token_data
            _reset_area_token_lookup.pop((user_id, token), None)


async def handle_help() -> str:
    """Return help text."""
    return HELP_TEXT


async def handle_clear(user_id: uuid.UUID) -> str:
    """Clear all conversation history for a user."""
    histories = await db.HistoriesManager.list_by_user(user_id)
    if not histories:
        return "No conversation history to clear."

    async with transaction() as conn:
        for h in histories:
            await db.HistoriesManager.delete(h.id, conn=conn, auto_commit=False)

    return f"Cleared {len(histories)} conversation(s)."


async def handle_delete_init(user_id: uuid.UUID) -> str:
    """Initialize deletion by generating a confirmation token."""
    _cleanup_expired_tokens()

    token = secrets.token_hex(4)
    _delete_tokens[user_id] = (token, time.time())

    return (
        f"WARNING: This will permanently delete your account and all data.\n"
        f"To confirm, type: /delete_{token}\n"
        f"This token expires in 60 seconds."
    )


async def handle_delete_confirm(user_id: uuid.UUID, token: str) -> str:
    """Confirm deletion with token and delete all user data."""
    _cleanup_expired_tokens()

    stored = _delete_tokens.pop(user_id, None)
    if stored is None:
        return "No pending deletion. Use /delete first."

    stored_token, _ = stored
    if token != stored_token:
        return "Invalid token. Use /delete to get a new token."

    await _delete_user_data(user_id)
    return "Account and all data deleted."


async def _delete_knowledge(user_id: uuid.UUID, conn: aiosqlite.Connection) -> None:
    """Delete user knowledge items."""
    items = await db.UserKnowledgeManager.list_by_user(user_id, conn)
    for item in items:
        await db.UserKnowledgeManager.delete(item.id, conn=conn, auto_commit=False)


async def _delete_area_data(area_id: uuid.UUID, conn: aiosqlite.Connection) -> None:
    """Delete all data for a single area (leaf history, summaries, coverage)."""
    descendants = await db.LifeAreasManager.get_descendants(area_id, conn)
    leaf_ids = [d.id for d in descendants]
    leaf_ids.append(area_id)  # Include root area itself if it's a leaf
    for leaf_id in leaf_ids:
        await db.LeafHistoryManager.delete_by_leaf(leaf_id, conn)
        await db.SummariesManager.delete_by_area(leaf_id, conn)
        await db.LifeAreasManager.set_covered_at(leaf_id, None, conn)


async def _delete_api_keys(user_id: uuid.UUID, conn: aiosqlite.Connection) -> None:
    """Delete all API keys for a user."""
    keys = await db.ApiKeysManager.list_by_user(user_id, conn)
    for ak in keys:
        await db.ApiKeysManager.delete(ak.id, conn=conn, auto_commit=False)


async def _delete_user_data(user_id: uuid.UUID) -> None:
    """Delete all data for a user in FK-safe order."""
    async with transaction() as conn:
        await _delete_knowledge(user_id, conn)

        areas = await db.LifeAreasManager.list_by_user(user_id, conn)
        for area in areas:
            await _delete_area_data(area.id, conn)

        for area in areas:
            await db.LifeAreasManager.delete(area.id, conn=conn, auto_commit=False)

        histories = await db.HistoriesManager.list_by_user(user_id, conn)
        for h in histories:
            await db.HistoriesManager.delete(h.id, conn=conn, auto_commit=False)

        await _delete_api_keys(user_id, conn)
        await db.UsersManager.delete(user_id, conn=conn, auto_commit=False)


async def handle_mode_show(user: User) -> str:
    """Show current input mode."""
    mode_descriptions = {
        InputMode.auto: "auto (automatically routes to interview or areas)",
        InputMode.conduct_interview: "interview (conduct interviews)",
        InputMode.manage_areas: "areas (manage life areas)",
    }
    desc = mode_descriptions.get(user.mode, user.mode.value)
    return f"Current mode: {desc}"


async def handle_mode_set(user: User, mode_name: str) -> str:
    """Set input mode."""
    mode_map = {
        "auto": InputMode.auto,
        "interview": InputMode.conduct_interview,
        "areas": InputMode.manage_areas,
    }

    mode = mode_map.get(mode_name.lower())
    if mode is None:
        valid = ", ".join(mode_map.keys())
        return f"Unknown mode: {mode_name}. Valid modes: {valid}"

    db_user = await db.UsersManager.get_by_id(user.id)
    if db_user is None:
        return "User not found."

    updated = db.User(
        id=db_user.id,
        name=db_user.name,
        mode=mode.value,
        current_area_id=db_user.current_area_id,
    )
    await db.UsersManager.update(user.id, updated)

    return f"Mode changed to: {mode_name}"


def _validate_reset_area(
    area: db.LifeArea | None, user_id: uuid.UUID, area_id_str: str
) -> str | None:
    """Validate area for reset. Returns error message or None if valid."""
    if area is None:
        return f"Area not found: {area_id_str}"
    if area.user_id != user_id:
        return "You don't have permission to reset this area."
    return None


async def handle_reset_area_init(user_id: uuid.UUID, area_id_str: str) -> str:
    """Initialize area reset by generating a confirmation token."""
    _cleanup_expired_reset_tokens()

    try:
        area_id = uuid.UUID(area_id_str)
    except ValueError:
        return f"Invalid area ID: {area_id_str}"

    area = await db.LifeAreasManager.get_by_id(area_id)
    if error := _validate_reset_area(area, user_id, area_id_str):
        return error

    token = secrets.token_hex(4)
    _reset_area_tokens[(user_id, area_id)] = (token, time.time())
    _reset_area_token_lookup[(user_id, token)] = area_id

    return (
        f"This will delete extracted knowledge and summaries for '{area.title}'.\n"
        f"To confirm, type: /reset_area_{token}\n"
        f"This token expires in 60 seconds."
    )


async def handle_reset_area_confirm(user_id: uuid.UUID, token: str) -> str:
    """Confirm area reset with token and delete extracted data."""
    _cleanup_expired_reset_tokens()

    # O(1) lookup using reverse mapping
    area_id = _reset_area_token_lookup.pop((user_id, token), None)
    if area_id is None:
        return "Invalid or expired token. Use /reset_area_<area-id> to start over."

    _reset_area_tokens.pop((user_id, area_id), None)

    async with transaction() as conn:
        await _delete_area_data(area_id, conn)

    area = await db.LifeAreasManager.get_by_id(area_id)
    title = area.title if area else str(area_id)

    return f"Reset complete. Area '{title}' is ready for a new interview."


async def _keys_list(user_id: uuid.UUID) -> str:
    """List all API keys for a user (showing stored prefix)."""
    keys = await db.ApiKeysManager.list_by_user(user_id)
    if not keys:
        return "No API keys. Use /mcp_keys create <label> to create one."
    lines = [
        f"  {k.key_prefix}...  {k.label}  ({time.strftime('%Y-%m-%d', time.gmtime(k.created_at))})"
        for k in keys
    ]
    return "API keys:\n" + "\n".join(lines)


async def _keys_create(user_id: uuid.UUID, label: str) -> str:
    """Generate a new API key for a user."""
    from src.infrastructure.db.api_managers import hash_key
    from src.shared.ids import new_id

    label = label.strip()[:64]
    if not label:
        return "Label must not be empty."

    key = secrets.token_hex(32)
    api_key = db.ApiKey(
        id=new_id(),
        key_hash=hash_key(key),
        key_prefix=key[:8],
        user_id=user_id,
        label=label,
        created_at=time.time(),
    )
    await db.ApiKeysManager.create(api_key.id, api_key)
    return (
        f"Created API key '{label}':\n{key}\n\nSave this key — it won't be shown again."
    )


async def _keys_revoke(user_id: uuid.UUID, prefix: str) -> str:
    """Revoke an API key by prefix (min 8 chars)."""
    if len(prefix) < MIN_KEY_PREFIX:
        return "Prefix must be at least 8 characters."
    keys = await db.ApiKeysManager.list_by_user(user_id)
    matches = [k for k in keys if k.key_prefix == prefix[:MIN_KEY_PREFIX]]
    if not matches:
        return f"No key matching prefix '{prefix}'."
    if len(matches) > 1:
        return f"Prefix '{prefix}' matches multiple keys. Be more specific."
    await db.ApiKeysManager.delete(matches[0].id)
    return f"Revoked key {matches[0].key_prefix}... ({matches[0].label})."


_KEYS_USAGE = {
    "create": "Usage: /mcp_keys create <label>",
    "revoke": "Usage: /mcp_keys revoke <prefix>",
}

_KEYS_HANDLERS: dict[str, Callable[[uuid.UUID, str], Coroutine]] = {
    "create": _keys_create,
    "revoke": _keys_revoke,
}


async def handle_keys_command(user_id: uuid.UUID, arg: str | None) -> str:
    """Dispatch /mcp_keys subcommands."""
    if arg is None:
        return await _keys_list(user_id)
    parts = arg.split(maxsplit=1)
    sub = parts[0].lower()
    sub_arg = parts[1] if len(parts) > 1 else None
    handler = _KEYS_HANDLERS.get(sub)
    if handler is None:
        return "Unknown subcommand. Use: /mcp_keys [create <label> | revoke <prefix>]"
    if not sub_arg:
        return _KEYS_USAGE[sub]
    return await handler(user_id, sub_arg)


CommandHandler = Callable[[], Coroutine[None, None, str | None]]


async def handle_reset_area_current(user: User) -> str:
    """Handle /reset_area — reset the user's current area."""
    if user.current_life_area_id is None:
        return "No current area set. Select an area to interview first."
    return await handle_reset_area_init(user.id, str(user.current_life_area_id))


async def _handle_reset_area_command(user_id: uuid.UUID, value: str) -> str:
    """Handle /reset_area_ command - dispatches to init or confirm."""
    try:
        uuid.UUID(value)
        return await handle_reset_area_init(user_id, value)
    except ValueError:
        return await handle_reset_area_confirm(user_id, value)


async def process_command(text: str, user: User) -> str | None:
    """Process a command and return response, or None if not a command."""
    if not text.startswith("/"):
        return None

    parts = text.split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else None

    # Build dispatch table with closures
    handlers: dict[str, CommandHandler] = {
        "/help": handle_help,
        "/clear": lambda: handle_clear(user.id),
        "/delete": lambda: handle_delete_init(user.id),
        "/mode": lambda: handle_mode_set(user, arg) if arg else handle_mode_show(user),
        "/reset_area": lambda: handle_reset_area_current(user),
        "/mcp_keys": lambda: handle_keys_command(user.id, arg),
    }

    # Check exact match, then pattern-based commands
    if cmd in handlers:
        handler = handlers[cmd]
    elif cmd.startswith("/delete_"):
        handler = lambda: handle_delete_confirm(user.id, cmd[8:])
    elif cmd.startswith("/reset_area_"):
        handler = lambda: _handle_reset_area_command(user.id, cmd[12:])
    else:
        return None

    return await handler()
