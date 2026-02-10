"""Auth process: Exchange external IDs for internal user_ids."""

from src.processes.auth.interfaces import AuthRequest


# Lazy imports for worker functions to avoid circular imports
def resolve_user_id(provider: str, external_id: str):
    """Deterministic mapping from external ID to internal user_id."""
    from src.processes.auth.worker import resolve_user_id as _resolve_user_id

    return _resolve_user_id(provider, external_id)


def run_auth_pool(channels):
    """Run the auth worker pool."""
    from src.processes.auth.worker import run_auth_pool as _run_auth_pool

    return _run_auth_pool(channels)


__all__ = ["AuthRequest", "resolve_user_id", "run_auth_pool"]
