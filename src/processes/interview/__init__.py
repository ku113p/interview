"""Interview process: Main graph worker for message processing."""

from src.processes.interview.interfaces import ChannelRequest, ChannelResponse
from src.processes.interview.state import State, Target

# Lazy imports for graph-related items to avoid circular imports
# These are only needed at runtime, not during import


def get_graph():
    """Build and compile the main workflow graph."""
    from src.processes.interview.graph import get_graph as _get_graph

    return _get_graph()


def run_graph_pool(channels):
    """Run the graph worker pool."""
    from src.processes.interview.worker import run_graph_pool as _run_graph_pool

    return _run_graph_pool(channels)


def _init_graph_state(msg, user):
    """Initialize graph state and create temporary files for media processing."""
    from src.processes.interview.worker import (
        _init_graph_state as _init_graph_state_impl,
    )

    return _init_graph_state_impl(msg, user)


__all__ = [
    "ChannelRequest",
    "ChannelResponse",
    "State",
    "Target",
    "_init_graph_state",
    "get_graph",
    "run_graph_pool",
]
