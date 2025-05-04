"""Tests for news endpoints."""
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, AsyncMock

from app.api.v1.api import api_router
from app.db.models import User
from app.services.auth import AuthService
from app.services.news import NewsService
from app.models.schemas import NewsArticle


@pytest.fixture
def app() -> FastAPI:
    """Create a test FastAPI application."""
    app = FastAPI()
    app.include_router(api_router)
    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:  # type: ignore
    """Create a test client."""
    async with AsyncClient(
        app=app,
        base_url="http://test",
        headers={"Authorization": "Bearer test-token"}
    ) as client:
        yield client


@pytest.fixture
async def test_user(session: AsyncSession) -> User:
    """Create a test user."""
    user = User(email="test@example.com", firebase_uid="test-uid")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.fixture
def mock_auth_service(test_user: User):
    """Create a mock for AuthService."""
    mock_service = AsyncMock(spec=AuthService)
    mock_service.get_current_user.return_value = test_user
    with patch("app.services.auth.AuthService", return_value=mock_service):
        yield mock_service


@pytest.fixture
def mock_news_articles():
    """Fixture for mock news articles."""
    return [NewsArticle(
        title="Test Title",
        author="Test Author",
        description="Test Description",
        url="https://example.com/test-article",
        image_url="https://example.com/image.jpg",
        published_at="2024-01-01T00:00:00Z",
        source="Test Source",
    )]


@pytest.fixture
def mock_news_service(mock_news_articles):
    """Create a mock for NewsService."""
    mock_service = AsyncMock(spec=NewsService)
    mock_service.search_articles.return_value = mock_news_articles
    mock_service.get_top_headlines.return_value = mock_news_articles
    return mock_service


@pytest.mark.asyncio
async def test_search_news(
        client: AsyncClient,
        mock_auth_service,
        mock_news_service,
        mock_news_articles):
    """Test searching for news."""
    with patch("app.api.v1.endpoints.news.NewsService") as mock_service_class:
        mock_service_class.return_value.__aenter__.return_value = (
            mock_news_service
        )
        response = await client.get(
            "/api/v1/news/search",
            params={"query": "test"}
        )
        mock_news_service.search_articles.assert_called_once()
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Title"


@pytest.mark.asyncio
async def test_get_headlines(
        client: AsyncClient,
        mock_auth_service,
        mock_news_service,
        mock_news_articles):
    """Test getting headlines."""
    with patch("app.api.v1.endpoints.news.NewsService") as mock_service_class:
        mock_service_class.return_value.__aenter__.return_value = (
            mock_news_service
        )
        response = await client.get("/api/v1/news/headlines")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Title"
        mock_news_service.get_top_headlines.assert_called_once()


@pytest.mark.asyncio
async def test_search_news_invalid_params(
        client: AsyncClient,
        mock_auth_service):
    """Test searching for news with invalid parameters."""
    response = await client.get(
        "/api/v1/news/search",
        params={"page_size": 0}
    )
    assert response.status_code == 422
    data = response.json()
    assert any("page_size" in error["loc"] for error in data["detail"])


@pytest.mark.asyncio
async def test_get_headlines_invalid_params(
        client: AsyncClient,
        mock_auth_service):
    """Test getting headlines with invalid parameters."""
    response = await client.get(
        "/api/v1/news/headlines",
        params={"page_size": 101}
    )
    assert response.status_code == 422
