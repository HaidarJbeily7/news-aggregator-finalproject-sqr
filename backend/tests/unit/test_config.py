"""Tests for application configuration."""
from app.core.config import Settings


def test_settings_default_values():
    """Test default values in Settings."""
    settings = Settings(
        SECRET_KEY="test-secret",
        FIREBASE_CREDENTIALS_PATH="test-path",
        NEWS_API_KEY="test-api-key",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        TESTING=True,
    )

    assert settings.PROJECT_NAME == "News Aggregator"
    assert settings.VERSION == "0.1.0"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert settings.BACKEND_CORS_ORIGINS == ["*"]
    assert settings.RATE_LIMIT_MAX_REQUESTS == 1000
    assert settings.RATE_LIMIT_TIME_WINDOW == 10
    assert settings.CACHE_MAX_SIZE == 1000
    assert settings.CACHE_TTL == 300


def test_settings_custom_values():
    """Test custom values in Settings."""
    settings = Settings(
        SECRET_KEY="test-secret",
        FIREBASE_CREDENTIALS_PATH="test-path",
        NEWS_API_KEY="test-api-key",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        TESTING=True,
        RATE_LIMIT_MAX_REQUESTS=50,
        RATE_LIMIT_TIME_WINDOW=30,
        CACHE_MAX_SIZE=500,
        CACHE_TTL=150,
    )

    assert settings.RATE_LIMIT_MAX_REQUESTS == 50
    assert settings.RATE_LIMIT_TIME_WINDOW == 30
    assert settings.CACHE_MAX_SIZE == 500
    assert settings.CACHE_TTL == 150


def test_settings_cors_origins():
    """Test CORS origins configuration."""
    settings = Settings(
        SECRET_KEY="test-secret",
        FIREBASE_CREDENTIALS_PATH="test-path",
        NEWS_API_KEY="test-api-key",
        DATABASE_URL="sqlite+aiosqlite:///./test.db",
        TESTING=True,
        BACKEND_CORS_ORIGINS=["http://localhost:3000", "https://example.com"],
    )

    assert len(settings.BACKEND_CORS_ORIGINS) == 2
    assert "http://localhost:3000" in settings.BACKEND_CORS_ORIGINS
    assert "https://example.com" in settings.BACKEND_CORS_ORIGINS
