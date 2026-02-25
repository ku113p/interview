import time


def get_timestamp() -> float:
    """Get current timestamp in seconds with nanosecond precision.

    Returns:
        float: Current time in seconds
    """
    return time.time_ns() / 1_000_000_000
