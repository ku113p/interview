"""MCP server authentication middleware using contextvars."""

import contextvars
import uuid

from fastmcp.server.middleware import Middleware, MiddlewareContext

from src.infrastructure.db.api_managers import ApiKeysManager

_current_user_id: contextvars.ContextVar[uuid.UUID | None] = contextvars.ContextVar(
    "mcp_user_id", default=None
)


def get_user_id() -> uuid.UUID:
    """Get the authenticated user_id for the current request."""
    uid = _current_user_id.get()
    if uid is None:
        raise PermissionError("Not authenticated")
    return uid


class AuthMiddleware(Middleware):
    """Validate Bearer API key and set user_id in contextvars."""

    async def __call__(self, context: MiddlewareContext, call_next):
        ctx = context.fastmcp_context
        if not (ctx and ctx.request_context and ctx.request_context.request):
            raise PermissionError("No request context available")

        auth = ctx.request_context.request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            raise PermissionError("Missing Authorization: Bearer <key>")
        key = auth.removeprefix("Bearer ").strip()
        api_key = await ApiKeysManager.get_by_key(key)
        if api_key is None:
            raise PermissionError("Invalid API key")

        token = _current_user_id.set(api_key.user_id)
        try:
            return await call_next(context)
        finally:
            _current_user_id.reset(token)
