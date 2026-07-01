"""Application settings and configuration management using Pydantic."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # Application
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    log_format: str = "json"

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/labeling_db"

    # OpenAI / LLM
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 500

    # API Security
    api_key_secret: str = ""
    rate_limit_per_minute: int = 100

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
