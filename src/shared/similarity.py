"""Vector similarity utilities (pure Python, no extra dependencies)."""

import math


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def find_top_k(
    query_vec: list[float],
    candidates: list[tuple[str, list[float]]],
    k: int = 5,
) -> list[tuple[str, float]]:
    """Return top-k (id, score) pairs ranked by cosine similarity."""
    scored = [(cid, cosine_similarity(query_vec, vec)) for cid, vec in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
