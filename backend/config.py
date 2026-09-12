from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application configuration settings"""

    # Application
    APP_NAME: str = "RuralCare AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    # Default: SQLite for zero-setup local/hackathon demo. Set DATABASE_URL to a
    # postgresql:// DSN (see docker-compose.yml) for a production-style deployment.
    DATABASE_URL: str = "sqlite:///./ruralcare.db"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # GenAI (optional). If no credentials are supplied, the GenAI explanation
    # service transparently falls back to deterministic, template-based text.
    WATSONX_API_KEY: str = ""
    WATSONX_PROJECT_ID: str = ""
    WATSONX_URL: str = ""
    GENAI_PROVIDER: str = "template"  # "template" | "watsonx"

    # Data mode
    DEMO_MODE: bool = True  # True => data is clearly labeled DEMO DATA, not official statistics

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
