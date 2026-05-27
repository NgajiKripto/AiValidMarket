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

    # Security settings
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5001")
    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "60 per minute")
    RATE_LIMIT_VALIDATE = os.getenv("RATE_LIMIT_VALIDATE", "10 per minute")
    API_KEY = os.getenv("API_KEY", "")
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "10"))
    MAX_CONCURRENT_VALIDATIONS = int(os.getenv("MAX_CONCURRENT_VALIDATIONS", "5"))
    MAX_QUERY_LIMIT = int(os.getenv("MAX_QUERY_LIMIT", "100"))

    @classmethod
    def validate(cls):
        """Validate that required configuration is set."""
        if not cls.LLM_API_KEY:
            raise ValueError("LLM_API_KEY environment variable is required")
