import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional


class TaskStatus(Enum):
    """Status of an async task."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Represents an async task with status tracking."""
    id: str
    status: TaskStatus = TaskStatus.PENDING
    progress: int = 0
    message: str = ""
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self):
        """Convert task to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class TaskManager:
    """Thread-safe singleton for managing async tasks. Follows MiroFish pattern."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._tasks = {}
                    cls._instance._tasks_lock = threading.Lock()
        return cls._instance

    def create_task(self) -> Task:
        """Create a new task and return it."""
        task_id = str(uuid.uuid4())
        task = Task(id=task_id)
        with self._tasks_lock:
            self._tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        with self._tasks_lock:
            return self._tasks.get(task_id)

    def update_task(self, task_id: str, status: TaskStatus = None,
                    progress: int = None, message: str = None):
        """Update task fields."""
        with self._tasks_lock:
            task = self._tasks.get(task_id)
            if task:
                if status is not None:
                    task.status = status
                if progress is not None:
                    task.progress = progress
                if message is not None:
                    task.message = message
                task.updated_at = datetime.utcnow()

    def complete_task(self, task_id: str, result: Any):
        """Mark a task as completed with a result."""
        with self._tasks_lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = TaskStatus.COMPLETED
                task.progress = 100
                task.result = result
                task.message = "Completed"
                task.updated_at = datetime.utcnow()

    def fail_task(self, task_id: str, error_message: str):
        """Mark a task as failed with an error message."""
        with self._tasks_lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = TaskStatus.FAILED
                task.error = error_message
                task.message = "Failed"
                task.updated_at = datetime.utcnow()

    def list_tasks(self) -> list:
        """List all tasks."""
        with self._tasks_lock:
            return [task.to_dict() for task in self._tasks.values()]

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Remove tasks older than max_age_hours."""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        with self._tasks_lock:
            to_remove = [
                tid for tid, task in self._tasks.items()
                if task.created_at < cutoff
            ]
            for tid in to_remove:
                del self._tasks[tid]
