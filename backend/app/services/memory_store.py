import json
import os
import sqlite3
import threading
from datetime import datetime
from typing import Optional

from app.config import Config
from app.models.memory import MemoryEntry, MemoryType, Session


class MemoryStore:
    """Thread-safe singleton for SQLite-backed memory storage."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: Optional[str] = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._db_path = db_path or Config.MEMORY_DB_PATH
                    cls._instance._db_lock = threading.Lock()
                    cls._instance._init_db()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None

    def _get_connection(self) -> sqlite3.Connection:
        """Get a new database connection."""
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Create database tables if they don't exist."""
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True) if self._db_path != ":memory:" else None
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    importance REAL NOT NULL DEFAULT 0.5,
                    access_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    session_id TEXT,
                    tags_json TEXT NOT NULL DEFAULT '[]',
                    metadata_json TEXT NOT NULL DEFAULT '{}'
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    idea_text TEXT NOT NULL,
                    summary TEXT NOT NULL DEFAULT '',
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    status TEXT NOT NULL DEFAULT 'active'
                )
            """)
            conn.commit()

    def save_memory(self, entry: MemoryEntry) -> MemoryEntry:
        """Save a memory entry to the database."""
        with self._db_lock:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO memories
                    (id, content, summary, memory_type, importance, access_count,
                     created_at, last_accessed, session_id, tags_json, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.id,
                    entry.content,
                    entry.summary,
                    entry.memory_type.value,
                    entry.importance,
                    entry.access_count,
                    entry.created_at.isoformat(),
                    entry.last_accessed.isoformat(),
                    entry.session_id,
                    json.dumps(entry.tags),
                    json.dumps(entry.metadata),
                ))
                conn.commit()
        return entry

    def get_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get a memory entry by ID."""
        with self._db_lock:
            with self._get_connection() as conn:
                row = conn.execute(
                    "SELECT * FROM memories WHERE id = ?", (memory_id,)
                ).fetchone()
        if row is None:
            return None
        return self._row_to_memory(row)

    def list_memories(
        self,
        limit: int = 50,
        offset: int = 0,
        memory_type_filter: Optional[MemoryType] = None,
    ) -> list[MemoryEntry]:
        """List memories with optional type filter."""
        with self._db_lock:
            with self._get_connection() as conn:
                if memory_type_filter:
                    rows = conn.execute(
                        "SELECT * FROM memories WHERE memory_type = ? ORDER BY last_accessed DESC LIMIT ? OFFSET ?",
                        (memory_type_filter.value, limit, offset),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT * FROM memories ORDER BY last_accessed DESC LIMIT ? OFFSET ?",
                        (limit, offset),
                    ).fetchall()
        return [self._row_to_memory(row) for row in rows]

    def get_memories_for_search(self) -> list[MemoryEntry]:
        """Get all memories for search indexing."""
        with self._db_lock:
            with self._get_connection() as conn:
                rows = conn.execute("SELECT * FROM memories").fetchall()
        return [self._row_to_memory(row) for row in rows]

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory entry by ID."""
        with self._db_lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "DELETE FROM memories WHERE id = ?", (memory_id,)
                )
                conn.commit()
                return cursor.rowcount > 0

    def update_access(self, memory_id: str):
        """Update access count and last_accessed timestamp."""
        with self._db_lock:
            with self._get_connection() as conn:
                conn.execute("""
                    UPDATE memories
                    SET access_count = access_count + 1,
                        last_accessed = ?
                    WHERE id = ?
                """, (datetime.utcnow().isoformat(), memory_id))
                conn.commit()

    def save_session(self, session: Session) -> Session:
        """Save a session to the database."""
        with self._db_lock:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO sessions
                    (id, idea_text, summary, started_at, ended_at, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session.id,
                    session.idea_text,
                    session.summary,
                    session.started_at.isoformat(),
                    session.ended_at.isoformat() if session.ended_at else None,
                    session.status,
                ))
                conn.commit()
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        with self._db_lock:
            with self._get_connection() as conn:
                row = conn.execute(
                    "SELECT * FROM sessions WHERE id = ?", (session_id,)
                ).fetchone()
        if row is None:
            return None
        return self._row_to_session(row)

    def list_sessions(self, limit: int = 10, offset: int = 0) -> list[Session]:
        """List sessions ordered by most recent."""
        with self._db_lock:
            with self._get_connection() as conn:
                rows = conn.execute(
                    "SELECT * FROM sessions ORDER BY started_at DESC LIMIT ? OFFSET ?",
                    (limit, offset),
                ).fetchall()
        return [self._row_to_session(row) for row in rows]

    def get_stats(self) -> dict:
        """Get memory store statistics."""
        with self._db_lock:
            with self._get_connection() as conn:
                memory_count = conn.execute(
                    "SELECT COUNT(*) FROM memories"
                ).fetchone()[0]
                session_count = conn.execute(
                    "SELECT COUNT(*) FROM sessions"
                ).fetchone()[0]
                type_counts = {}
                for mt in MemoryType:
                    count = conn.execute(
                        "SELECT COUNT(*) FROM memories WHERE memory_type = ?",
                        (mt.value,),
                    ).fetchone()[0]
                    type_counts[mt.value] = count
        return {
            "total_memories": memory_count,
            "total_sessions": session_count,
            "memories_by_type": type_counts,
        }

    def _row_to_memory(self, row: sqlite3.Row) -> MemoryEntry:
        """Convert a database row to a MemoryEntry."""
        return MemoryEntry(
            id=row["id"],
            content=row["content"],
            summary=row["summary"],
            memory_type=MemoryType(row["memory_type"]),
            importance=row["importance"],
            access_count=row["access_count"],
            created_at=datetime.fromisoformat(row["created_at"]),
            last_accessed=datetime.fromisoformat(row["last_accessed"]),
            session_id=row["session_id"],
            tags=json.loads(row["tags_json"]),
            metadata=json.loads(row["metadata_json"]),
        )

    def _row_to_session(self, row: sqlite3.Row) -> Session:
        """Convert a database row to a Session."""
        return Session(
            id=row["id"],
            idea_text=row["idea_text"],
            summary=row["summary"],
            started_at=datetime.fromisoformat(row["started_at"]),
            ended_at=datetime.fromisoformat(row["ended_at"]) if row["ended_at"] else None,
            status=row["status"],
        )
