"""Unit tests for similarity utilities."""

import pytest
from src.shared.similarity import cosine_similarity, find_top_k


class TestCosineSimilarity:
    """Tests for cosine_similarity."""

    def test_identical_vectors(self):
        """Identical vectors should have similarity ~1.0."""
        vec = [1.0, 2.0, 3.0]
        assert cosine_similarity(vec, vec) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        """Orthogonal vectors should have similarity ~0.0."""
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert cosine_similarity(a, b) == pytest.approx(0.0)

    def test_zero_vector(self):
        """Zero vector should return 0.0."""
        zero = [0.0, 0.0, 0.0]
        other = [1.0, 2.0, 3.0]
        assert cosine_similarity(zero, other) == 0.0


class TestFindTopK:
    """Tests for find_top_k."""

    def test_basic_ranking(self):
        """Should return candidates ranked by similarity."""
        query = [1.0, 0.0]
        candidates = [
            ("a", [0.0, 1.0]),  # orthogonal
            ("b", [1.0, 0.0]),  # identical
            ("c", [0.7, 0.7]),  # diagonal
        ]
        results = find_top_k(query, candidates, k=3)
        ids = [r[0] for r in results]
        assert ids[0] == "b"  # most similar
        assert ids[-1] == "a"  # least similar

    def test_limits_results(self):
        """Should return at most k results."""
        query = [1.0, 0.0]
        candidates = [
            ("a", [1.0, 0.0]),
            ("b", [0.9, 0.1]),
            ("c", [0.8, 0.2]),
            ("d", [0.7, 0.3]),
        ]
        results = find_top_k(query, candidates, k=2)
        assert len(results) == 2

    def test_empty_candidates(self):
        """Empty candidates should return empty result."""
        results = find_top_k([1.0, 0.0], [], k=5)
        assert results == []
