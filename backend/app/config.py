import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (two levels up from this file)
project_root = Path(__file__).resolve().parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)


class Config:
    """Application configuration loaded from environment variables."""

    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-4o-mini")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    JSON_AS_ASCII = False

    MEMORY_DB_PATH = os.getenv(
        "MEMORY_DB_PATH",
        str(Path(__file__).resolve().parent.parent / "data" / "memory.sqlite"),
    )
    MEMORY_ENABLED = os.getenv("MEMORY_ENABLED", "true").lower() in ("true", "1", "yes")

    @classmethod
    def validate(cls):
        """Validate that required configuration is set."""
        if not cls.LLM_API_KEY:
            raise ValueError("LLM_API_KEY environment variable is required")
