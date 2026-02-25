"""Simple async TTL cache utilities."""

import time
from typing import TypeVar

T = TypeVar("T")


class TTLCache:
    """Simple TTL cache for async function results."""

    def __init__(self, ttl: float = 10.0):
        self._cache: dict[str, tuple[float, T]] = {}
        self._ttl = ttl

    def get(self, key: str) -> T | None:
        if key in self._cache:
            ts, value = self._cache[key]
            if time.time() - ts < self._ttl:
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value: T) -> None:
        self._cache[key] = (time.time(), value)
