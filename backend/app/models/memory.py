import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class MemoryType(Enum):
    """Types of memory entries."""
    OBSERVATION = "observation"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


@dataclass
class MemoryEntry:
    """A single memory entry with metadata."""
    id: str
    content: str
    summary: str
    memory_type: MemoryType
    importance: float = 0.5
    access_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "content": self.content,
            "summary": self.summary,
            "memory_type": self.memory_type.value,
            "importance": self.importance,
            "access_count": self.access_count,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "session_id": self.session_id,
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class Session:
    """Represents a validation session."""
    id: str
    idea_text: str
    summary: str = ""
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    status: str = "active"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "idea_text": self.idea_text,
            "summary": self.summary,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "status": self.status,
        }


@dataclass
class MemorySearchResult:
    """A memory search result with relevance score."""
    entry: MemoryEntry
    relevance_score: float

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "entry": self.entry.to_dict(),
            "relevance_score": self.relevance_score,
        }
