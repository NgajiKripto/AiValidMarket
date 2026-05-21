import threading
import uuid
from datetime import datetime
from typing import Optional

from app.models.memory import (
    MemoryEntry,
    MemorySearchResult,
    MemoryType,
    Session,
)
from app.services.memory_search import MemorySearchEngine
from app.services.memory_store import MemoryStore


class MemoryService:
    """Thread-safe singleton orchestrating memory storage, search, and decay."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: Optional[str] = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._store = MemoryStore(db_path)
                    cls._instance._search_engine = MemorySearchEngine()
                    cls._instance._service_lock = threading.Lock()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None

    def remember(
        self,
        content: str,
        memory_type: MemoryType,
        importance: float = 0.5,
        session_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> MemoryEntry:
        """Store a new memory entry."""
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            content=content,
            summary=content[:200] if len(content) > 200 else content,
            memory_type=memory_type,
            importance=max(0.0, min(1.0, importance)),
            access_count=0,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            session_id=session_id,
            tags=tags or [],
            metadata=metadata or {},
        )
        with self._service_lock:
            self._store.save_memory(entry)
        return entry

    def recall(
        self,
        query: str,
        limit: int = 5,
        memory_type_filter: Optional[MemoryType] = None,
    ) -> list[MemorySearchResult]:
        """Search memories by relevance to query."""
        with self._service_lock:
            memories = self._store.get_memories_for_search()

        if memory_type_filter:
            memories = [
                m for m in memories if m.memory_type == memory_type_filter
            ]

        results = self._search_engine.search(query, memories, top_k=limit)

        search_results = []
        for memory_id, score in results:
            with self._service_lock:
                self._store.update_access(memory_id)
                entry = self._store.get_memory(memory_id)
            if entry:
                search_results.append(
                    MemorySearchResult(entry=entry, relevance_score=score)
                )

        return search_results

    def forget(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        with self._service_lock:
            return self._store.delete_memory(memory_id)

    def get_session_history(self, limit: int = 10) -> list[Session]:
        """Get recent sessions."""
        with self._service_lock:
            return self._store.list_sessions(limit=limit)

    def start_session(self, idea_text: str) -> Session:
        """Start a new validation session."""
        session = Session(
            id=str(uuid.uuid4()),
            idea_text=idea_text,
            started_at=datetime.utcnow(),
            status="active",
        )
        with self._service_lock:
            self._store.save_session(session)
        return session

    def end_session(self, session_id: str, summary: str) -> Session:
        """End a session with a summary."""
        with self._service_lock:
            session = self._store.get_session(session_id)
            if session is None:
                raise ValueError(f"Session not found: {session_id}")
            session.ended_at = datetime.utcnow()
            session.summary = summary
            session.status = "completed"
            self._store.save_session(session)
        return session

    def consolidate(self):
        """Apply memory decay and remove low-importance memories."""
        with self._service_lock:
            memories = self._store.get_memories_for_search()

        now = datetime.utcnow()
        to_delete = []

        for memory in memories:
            hours_since_access = (
                now - memory.last_accessed
            ).total_seconds() / 3600.0

            # Apply exponential decay based on time
            new_importance = memory.importance * (0.95 ** (hours_since_access / 24.0))

            # Boost frequently accessed memories
            new_importance += 0.01 * memory.access_count
            new_importance = min(1.0, new_importance)

            if new_importance < 0.1:
                to_delete.append(memory.id)
            else:
                memory.importance = new_importance
                with self._service_lock:
                    self._store.save_memory(memory)

        for memory_id in to_delete:
            with self._service_lock:
                self._store.delete_memory(memory_id)

    def inject_context(self, query: str) -> str:
        """Search memories and format results as LLM context block."""
        results = self.recall(query, limit=3)

        if not results:
            return ""

        lines = ["## Relevant Past Insights"]
        for result in results:
            entry = result.entry
            score = result.relevance_score
            lines.append(
                f"- [{entry.memory_type.value}] (score: {score:.2f}): {entry.summary}"
            )

        return "\n".join(lines)

    def get_stats(self) -> dict:
        """Get memory system statistics."""
        with self._service_lock:
            return self._store.get_stats()
