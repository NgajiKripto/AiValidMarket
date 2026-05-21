import re

from rank_bm25 import BM25Plus

from app.models.memory import MemoryEntry


class MemorySearchEngine:
    """BM25-based search engine for memory entries."""

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text by lowercasing and splitting on non-alphanumeric chars."""
        return [
            token
            for token in re.split(r"[^a-z0-9]+", text.lower())
            if token
        ]

    def search(
        self, query: str, memories: list[MemoryEntry], top_k: int = 5
    ) -> list[tuple[str, float]]:
        """Search memories using BM25 ranking.

        Returns a list of (memory_id, score) tuples sorted by relevance.
        """
        if not memories:
            return []

        corpus = [
            self._tokenize(f"{m.content} {m.summary} {' '.join(m.tags)}")
            for m in memories
        ]

        # Filter out empty token lists
        valid_indices = [i for i, tokens in enumerate(corpus) if tokens]
        if not valid_indices:
            return []

        valid_corpus = [corpus[i] for i in valid_indices]
        valid_memories = [memories[i] for i in valid_indices]

        bm25 = BM25Plus(valid_corpus)
        query_tokens = self._tokenize(query)

        if not query_tokens:
            return []

        scores = bm25.get_scores(query_tokens)

        # Find max score to determine relative threshold
        max_score = float(max(scores)) if len(scores) > 0 else 0.0
        if max_score <= 0:
            return []

        # Pair memories with scores and sort by relevance
        # Only include results with positive scores
        results = [
            (valid_memories[i].id, float(scores[i]))
            for i in range(len(valid_memories))
            if scores[i] > 0
        ]
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]
