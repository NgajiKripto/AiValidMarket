import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.memory import MemoryType


class TestMemoryAPI:
    """Tests for the memory API endpoints."""

    def setup_method(self):
        """Set up test fixtures with a temporary database."""
        from app.services.memory_service import MemoryService
        from app.services.memory_store import MemoryStore

        # Reset singletons before creating with temp DB
        MemoryService.reset_instance()
        MemoryStore.reset_instance()

        self.tmp_file = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
        self.tmp_path = self.tmp_file.name
        self.tmp_file.close()

        # Patch config before any singleton creation
        self.config_patcher = patch("app.config.Config.MEMORY_DB_PATH", self.tmp_path)
        self.config_patcher.start()

        # Now create the memory service (which also creates the store)
        self.memory_service = MemoryService(self.tmp_path)

        # Patch the module-level memory_service in both API modules
        import app.api.memory as memory_mod
        import app.api.validation as validation_mod
        self.mem_api_patcher = patch.object(memory_mod, "memory_service", self.memory_service)
        self.val_api_patcher = patch.object(validation_mod, "memory_service", self.memory_service)
        self.mem_api_patcher.start()
        self.val_api_patcher.start()

        from app import create_app
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def teardown_method(self):
        """Clean up singletons after each test."""
        self.mem_api_patcher.stop()
        self.val_api_patcher.stop()
        self.config_patcher.stop()

        from app.services.memory_service import MemoryService
        from app.services.memory_store import MemoryStore
        MemoryService.reset_instance()
        MemoryStore.reset_instance()

        try:
            os.unlink(self.tmp_path)
        except OSError:
            pass

    def test_get_sessions_returns_list(self):
        """Test GET /api/memory/sessions returns 200 with a list."""
        response = self.client.get("/api/memory/sessions")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_get_sessions_with_data(self):
        """Test GET /api/memory/sessions returns sessions that were created."""
        self.memory_service.start_session("Test idea for session")
        response = self.client.get("/api/memory/sessions")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1
        assert data[0]["idea_text"] == "Test idea for session"

    def test_get_session_detail(self):
        """Test GET /api/memory/sessions/<id> returns session detail."""
        session = self.memory_service.start_session("Detail test idea")
        response = self.client.get(f"/api/memory/sessions/{session.id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == session.id
        assert data["idea_text"] == "Detail test idea"

    def test_get_session_not_found(self):
        """Test GET /api/memory/sessions/<id> returns 404 for unknown session."""
        response = self.client.get("/api/memory/sessions/nonexistent-id")
        assert response.status_code == 404

    def test_search_memories_returns_results(self):
        """Test POST /api/memory/search returns 200 with results."""
        # Store some memories first
        self.memory_service.remember(
            content="AI-powered code review platform validation",
            memory_type=MemoryType.SEMANTIC,
            importance=0.7,
            tags=["AI", "code-review"],
        )
        response = self.client.post(
            "/api/memory/search",
            json={"query": "AI code review", "limit": 5},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "entry" in data[0]
        assert "relevance_score" in data[0]

    def test_search_memories_missing_query(self):
        """Test POST /api/memory/search returns 400 without query."""
        response = self.client.post(
            "/api/memory/search",
            json={},
        )
        assert response.status_code == 400

    def test_search_memories_with_type_filter(self):
        """Test POST /api/memory/search with type filter."""
        self.memory_service.remember(
            content="Observation about market trends",
            memory_type=MemoryType.OBSERVATION,
            importance=0.5,
        )
        self.memory_service.remember(
            content="Semantic knowledge about AI market",
            memory_type=MemoryType.SEMANTIC,
            importance=0.7,
        )
        response = self.client.post(
            "/api/memory/search",
            json={"query": "market", "type": "semantic"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        for result in data:
            assert result["entry"]["memory_type"] == "semantic"

    def test_get_stats_returns_counts(self):
        """Test GET /api/memory/stats returns 200 with counts."""
        response = self.client.get("/api/memory/stats")
        assert response.status_code == 200
        data = response.get_json()
        assert "total_memories" in data
        assert "total_sessions" in data
        assert "memories_by_type" in data

    def test_delete_memory_returns_result(self):
        """Test DELETE /api/memory/<id> returns deleted status."""
        entry = self.memory_service.remember(
            content="Memory to delete",
            memory_type=MemoryType.OBSERVATION,
            importance=0.5,
        )
        response = self.client.delete(f"/api/memory/{entry.id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["deleted"] is True

    def test_delete_nonexistent_memory(self):
        """Test DELETE /api/memory/<id> returns false for nonexistent."""
        response = self.client.delete("/api/memory/nonexistent-id")
        assert response.status_code == 200
        data = response.get_json()
        assert data["deleted"] is False
