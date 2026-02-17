"""Extract process: Knowledge extraction from completed areas."""

from src.processes.extract.interfaces import ExtractTask, SummaryVectorizeTask


# Lazy import for worker function to avoid circular imports
def run_extract_pool(channels):
    """Run the extract worker pool."""
    from src.processes.extract.worker import run_extract_pool as _run_extract_pool

    return _run_extract_pool(channels)


__all__ = ["ExtractTask", "SummaryVectorizeTask", "run_extract_pool"]
