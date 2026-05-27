import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app


class TestAPI:
    """Tests for the Flask API endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_health_endpoint(self):
        """Test the /health endpoint returns 200 with expected data."""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"
        assert data["service"] == "aivalidmarket-backend"

    def test_validate_endpoint_returns_task_id(self):
        """Test POST /api/validation/validate returns a task_id."""
        with patch("app.api.validation.executor") as mock_executor:
            mock_executor.submit = MagicMock()

            response = self.client.post(
                "/api/validation/validate",
                json={"idea": "A platform for AI-powered code review"},
            )

            assert response.status_code == 202
            data = response.get_json()
            assert "task_id" in data
            assert "status" in data
            assert data["status"] == "pending"
            mock_executor.submit.assert_called_once()

    def test_validate_endpoint_missing_idea(self):
        """Test POST /api/validation/validate returns 400 without idea."""
        response = self.client.post(
            "/api/validation/validate",
            json={},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_status_endpoint_not_found(self):
        """Test GET /api/validation/status/<id> returns 404 for unknown task."""
        response = self.client.get("/api/validation/status/nonexistent-id")
        assert response.status_code == 404

    def test_result_endpoint_not_found(self):
        """Test GET /api/validation/result/<id> returns 404 for unknown task."""
        response = self.client.get("/api/validation/result/nonexistent-id")
        assert response.status_code == 404
