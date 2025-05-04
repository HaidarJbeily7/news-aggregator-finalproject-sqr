"""Configuration settings for the application."""
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Project settings
    PROJECT_NAME: str = "News Aggregator"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = """
    AI-powered news aggregator with user authentication and customization
    """

    # API Settings
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Firebase
    FIREBASE_CREDENTIALS_PATH: str

    # News API
    NEWS_API_KEY: str

    # Database
    DATABASE_URL: str

    # Rate limiting settings
    RATE_LIMIT_MAX_REQUESTS: int = 100
    RATE_LIMIT_TIME_WINDOW: int = 60

    # Cache settings
    CACHE_MAX_SIZE: int = 1000
    CACHE_TTL: int = 300

    TESTING: bool

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


settings = Settings()
