"""Tests for the news service."""
import pytest
from unittest.mock import patch, MagicMock

from app.services.news import (
    NewsService,
    NewsSearchParams,
    create_news_api_client,
)


@pytest.fixture
def mock_news_response():
    """Fixture for mock news response."""
    return {
        "articles": [
            {
                "author": "Test Author",
                "description": "Test Description",
                "publishedAt": "2024-01-01T00:00:00Z",
                "source": "Test Source",
                "title": "Test Title",
                "url": "https://example.com/test-article",
                "urlToImage": "https://example.com/image.jpg",
            }
        ],
        "status": "ok",
        "totalResults": 1,
    }


@pytest.mark.asyncio
async def test_search_articles(mock_news_response):
    """Test searching for news articles."""
    mock_client = MagicMock()
    mock_client.get_everything.return_value = mock_news_response

    with patch("app.services.news.NewsApiClient", return_value=mock_client):
        async with NewsService() as news_service:
            params = NewsSearchParams(
                query="test",
                category="technology",
                page_size=10,
                page=1,
            )
            articles = await news_service.search_articles(params)

            assert len(articles) == 1
            article = articles[0]
            assert article.title == "Test Title"
            assert article.author == "Test Author"
            assert article.source == "Test Source"


@pytest.mark.asyncio
async def test_get_top_headlines(mock_news_response):
    """Test getting top headlines."""
    mock_client = MagicMock()
    mock_client.get_top_headlines.return_value = mock_news_response

    with patch("app.services.news.NewsApiClient", return_value=mock_client):
        async with NewsService() as news_service:
            articles = await news_service.get_top_headlines(
                category="technology",
                country="us",
                page_size=10,
            )

            assert len(articles) == 1
            article = articles[0]
            assert article.title == "Test Title"
            assert article.author == "Test Author"
            assert article.source == "Test Source"


def test_create_news_api_client():
    """Test creating a NewsApiClient instance."""
    client = create_news_api_client("test-api-key")
    assert client is not None


@pytest.mark.asyncio
async def test_news_service_error_handling():
    """Test error handling in news service."""
    mock_client = MagicMock()
    mock_client.get_everything.side_effect = Exception("API Error")

    with patch("app.services.news.NewsApiClient", return_value=mock_client):
        async with NewsService() as news_service:
            params = NewsSearchParams(query="test")
            with pytest.raises(Exception) as exc_info:
                await news_service.search_articles(params)
            assert "Error fetching news" in str(exc_info.value)


@pytest.mark.asyncio
async def test_news_service_context_manager():
    """Test news service context manager."""
    async with NewsService() as news_service:
        assert isinstance(news_service, NewsService)
