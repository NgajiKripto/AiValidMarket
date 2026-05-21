import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.memory import MemoryEntry, MemoryType, Session
from app.services.memory_search import MemorySearchEngine
from app.services.memory_service import MemoryService
from app.services.memory_store import MemoryStore


class TestMemoryStore:
    """Tests for the SQLite memory store."""

    def setup_method(self):
        """Set up a fresh store with a temp db for each test."""
        MemoryStore.reset_instance()
        self.tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
        self.store = MemoryStore(self.tmp.name)

    def teardown_method(self):
        """Clean up singleton."""
        MemoryStore.reset_instance()

    def test_save_and_retrieve_memory(self):
        """Test saving and retrieving a memory entry."""
        entry = MemoryEntry(
            id="test-1",
            content="The market for AI tutoring is growing fast",
            summary="AI tutoring market growth",
            memory_type=MemoryType.OBSERVATION,
            importance=0.7,
            access_count=0,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            tags=["market", "AI"],
            metadata={"source": "analysis"},
        )
        self.store.save_memory(entry)

        retrieved = self.store.get_memory("test-1")
        assert retrieved is not None
        assert retrieved.id == "test-1"
        assert retrieved.content == "The market for AI tutoring is growing fast"
        assert retrieved.memory_type == MemoryType.OBSERVATION
        assert retrieved.importance == 0.7
        assert retrieved.tags == ["market", "AI"]
        assert retrieved.metadata == {"source": "analysis"}

    def test_delete_memory(self):
        """Test deleting a memory entry."""
        entry = MemoryEntry(
            id="test-del",
            content="To be deleted",
            summary="delete me",
            memory_type=MemoryType.EPISODIC,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
        )
        self.store.save_memory(entry)
        assert self.store.delete_memory("test-del") is True
        assert self.store.get_memory("test-del") is None

    def test_get_stats(self):
        """Test statistics reporting."""
        entry = MemoryEntry(
            id="stat-1",
            content="Test content",
            summary="Test",
            memory_type=MemoryType.SEMANTIC,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
        )
        self.store.save_memory(entry)

        stats = self.store.get_stats()
        assert stats["total_memories"] == 1
        assert stats["total_sessions"] == 0
        assert stats["memories_by_type"]["semantic"] == 1


class TestMemorySearchEngine:
    """Tests for BM25 search."""

    def setup_method(self):
        self.engine = MemorySearchEngine()

    def test_search_finds_relevant_results(self):
        """Test that BM25 search returns relevant memories."""
        memories = [
            MemoryEntry(
                id="m1",
                content="Python is a programming language used for data science",
                summary="Python for data science",
                memory_type=MemoryType.SEMANTIC,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                tags=["python", "data"],
            ),
            MemoryEntry(
                id="m2",
                content="The restaurant serves great Italian food and pizza",
                summary="Italian restaurant review",
                memory_type=MemoryType.EPISODIC,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                tags=["food"],
            ),
            MemoryEntry(
                id="m3",
                content="Machine learning models need training data to function",
                summary="ML training data",
                memory_type=MemoryType.SEMANTIC,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                tags=["ml", "data"],
            ),
        ]

        results = self.engine.search("data science programming", memories)
        assert len(results) > 0
        # The most relevant result should be m1 (Python/data science)
        assert results[0][0] == "m1"

    def test_search_empty_corpus(self):
        """Test search with no memories returns empty list."""
        results = self.engine.search("test query", [])
        assert results == []

    def test_search_empty_query(self):
        """Test search with empty query returns empty list."""
        memories = [
            MemoryEntry(
                id="m1",
                content="Some content",
                summary="Summary",
                memory_type=MemoryType.OBSERVATION,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
            ),
        ]
        results = self.engine.search("", memories)
        assert results == []


class TestMemoryService:
    """Tests for the high-level memory service."""

    def setup_method(self):
        """Set up a fresh service with temp db."""
        MemoryService.reset_instance()
        MemoryStore.reset_instance()
        self.tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
        self.service = MemoryService(self.tmp.name)

    def teardown_method(self):
        """Clean up singletons."""
        MemoryService.reset_instance()
        MemoryStore.reset_instance()

    def test_remember_and_recall(self):
        """Test storing a memory and retrieving it via search."""
        self.service.remember(
            content="Flask is great for building REST APIs",
            memory_type=MemoryType.SEMANTIC,
            importance=0.8,
            tags=["flask", "api"],
        )
        self.service.remember(
            content="Vue 3 uses the composition API for better reactivity",
            memory_type=MemoryType.SEMANTIC,
            importance=0.6,
            tags=["vue", "frontend"],
        )

        results = self.service.recall("flask REST API")
        assert len(results) > 0
        assert results[0].entry.content == "Flask is great for building REST APIs"
        assert results[0].relevance_score > 0

    def test_forget(self):
        """Test deleting a memory."""
        entry = self.service.remember(
            content="Temporary note",
            memory_type=MemoryType.OBSERVATION,
        )
        assert self.service.forget(entry.id) is True
        results = self.service.recall("temporary note")
        assert len(results) == 0

    def test_memory_decay(self):
        """Test that consolidate reduces importance of old memories."""
        entry = self.service.remember(
            content="Old memory that should decay",
            memory_type=MemoryType.OBSERVATION,
            importance=0.5,
        )
        # Manually set last_accessed to 10 days ago
        entry.last_accessed = datetime.utcnow() - timedelta(days=10)
        self.service._store.save_memory(entry)

        self.service.consolidate()

        updated = self.service._store.get_memory(entry.id)
        # After 10 days of decay: 0.5 * 0.95^10 = ~0.299
        # With 0 access_count boost: stays ~0.299
        assert updated is not None
        assert updated.importance < 0.5

    def test_memory_decay_deletes_low_importance(self):
        """Test that consolidate deletes memories below threshold."""
        entry = self.service.remember(
            content="Very old unimportant memory",
            memory_type=MemoryType.OBSERVATION,
            importance=0.15,
        )
        # Set last_accessed far in the past so decay drops below 0.1
        entry.last_accessed = datetime.utcnow() - timedelta(days=30)
        self.service._store.save_memory(entry)

        self.service.consolidate()

        deleted = self.service._store.get_memory(entry.id)
        assert deleted is None

    def test_session_lifecycle(self):
        """Test starting and ending a session."""
        session = self.service.start_session("An AI tutoring platform")
        assert session.idea_text == "An AI tutoring platform"
        assert session.status == "active"
        assert session.ended_at is None

        ended = self.service.end_session(session.id, "Validated - strong market fit")
        assert ended.status == "completed"
        assert ended.summary == "Validated - strong market fit"
        assert ended.ended_at is not None

    def test_inject_context_returns_formatted_string(self):
        """Test that inject_context formats search results properly."""
        self.service.remember(
            content="The edtech market is worth $300B globally",
            memory_type=MemoryType.OBSERVATION,
            importance=0.9,
            tags=["edtech", "market"],
        )
        self.service.remember(
            content="SaaS retention is key for B2B products",
            memory_type=MemoryType.SEMANTIC,
            importance=0.7,
            tags=["saas", "retention"],
        )

        context = self.service.inject_context("edtech market size")
        assert "## Relevant Past Insights" in context
        assert "[observation]" in context
        assert "score:" in context

    def test_inject_context_empty_when_no_results(self):
        """Test inject_context returns empty string with no matches."""
        context = self.service.inject_context("completely unrelated xyz123")
        assert context == ""

    def test_get_stats(self):
        """Test statistics include correct counts."""
        self.service.remember(
            content="Stat memory 1",
            memory_type=MemoryType.OBSERVATION,
        )
        self.service.remember(
            content="Stat memory 2",
            memory_type=MemoryType.SEMANTIC,
        )
        self.service.start_session("Test idea")

        stats = self.service.get_stats()
        assert stats["total_memories"] == 2
        assert stats["total_sessions"] == 1
        assert stats["memories_by_type"]["observation"] == 1
        assert stats["memories_by_type"]["semantic"] == 1

    def test_get_session_history(self):
        """Test retrieving session history."""
        self.service.start_session("Idea 1")
        self.service.start_session("Idea 2")

        history = self.service.get_session_history(limit=10)
        assert len(history) == 2
