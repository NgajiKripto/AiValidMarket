import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.idea_analyzer import IdeaAnalyzer


class TestIdeaAnalyzer:
    """Tests for IdeaAnalyzer service with mocked LLM client."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm = MagicMock()
        self.analyzer = IdeaAnalyzer(self.mock_llm)

    def test_analyze_idea_returns_expected_structure(self):
        """Test that analyze_idea returns proper structure from LLM response."""
        expected_response = {
            "market_assessment": "The AI tutoring market is growing rapidly.",
            "keywords": [
                "AI tutor", "online learning", "edtech", "personalized learning",
                "AI education", "tutoring platform", "adaptive learning",
                "student engagement", "homework help", "study assistant",
            ],
            "questions": [
                "How effective is AI tutoring?",
                "What are the best AI tutoring platforms?",
                "Can AI replace human tutors?",
                "How much does AI tutoring cost?",
                "Is AI tutoring safe for children?",
                "What subjects can AI tutor?",
                "How does AI tutoring work?",
                "What are the limitations of AI tutors?",
            ],
            "categories": ["EdTech", "AI/ML", "SaaS", "B2C"],
            "target_audience": "Students aged 12-25 and their parents",
            "competitors_hints": [
                "AI tutoring startups",
                "Khan Academy AI",
                "Chegg alternatives",
                "online tutoring market leaders",
                "AI homework help apps",
            ],
        }
        self.mock_llm.chat_json.return_value = expected_response

        result = self.analyzer.analyze_idea("An AI-powered tutoring platform")

        assert result == expected_response
        assert "market_assessment" in result
        assert "keywords" in result
        assert "questions" in result
        assert "categories" in result
        assert "target_audience" in result
        assert "competitors_hints" in result
        assert len(result["keywords"]) == 10
        assert len(result["questions"]) == 8

    def test_analyze_idea_calls_llm_with_correct_params(self):
        """Test that the LLM client is called with proper messages."""
        self.mock_llm.chat_json.return_value = {"market_assessment": "test"}

        self.analyzer.analyze_idea("A food delivery app")

        self.mock_llm.chat_json.assert_called_once()
        call_args = self.mock_llm.chat_json.call_args
        messages = call_args[0][0]

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert "A food delivery app" in messages[1]["content"]

    def test_analyze_idea_raises_on_llm_error(self):
        """Test that LLM errors are propagated."""
        self.mock_llm.chat_json.side_effect = Exception("API error")

        try:
            self.analyzer.analyze_idea("Some idea")
            assert False, "Should have raised an exception"
        except Exception as e:
            assert "API error" in str(e)
