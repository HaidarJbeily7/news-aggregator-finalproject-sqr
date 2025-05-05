"""News service for fetching and searching news articles."""
from typing import List
from newsapi import NewsApiClient
from app.core.config import settings
from app.models.schemas import NewsArticle, NewsSearchParams


class NewsServiceError(Exception):
    """Exception raised for errors in the NewsService."""
    pass


def create_news_api_client(api_key: str) -> NewsApiClient:
    """Create a NewsApiClient instance."""
    return NewsApiClient(api_key=api_key)


def convert_api_response_to_articles(response: dict) -> List[NewsArticle]:
    """Convert NewsAPI response to list of NewsArticle models."""
    return [
        NewsArticle(**article)
        for article in response["articles"]
    ]


class NewsService:
    """Service for interacting with the News API."""

    def __init__(self) -> None:
        """Initialize the NewsService."""
        self.api_key = settings.NEWS_API_KEY
        self.client = create_news_api_client(self.api_key)

    async def search_articles(
        self,
        params: NewsSearchParams,
    ) -> List[NewsArticle]:
        """Search for news articles."""
        try:
            # Build query string to include category if provided
            q = params.query or ""
            if params.category:
                category_str = f"category:{params.category}"
                q = f"{q} {category_str}" if q else category_str

            response = self.client.get_everything(
                q=q.strip() or None,  # Use None if empty string
                language=params.language,
                page_size=params.page_size,
                page=params.page,
            )
            return convert_api_response_to_articles(response)
        except Exception as e:
            raise NewsServiceError(f"Error fetching news: {str(e)}")

    async def get_top_headlines(
        self,
        category: str | None = None,
        country: str = "us",
        page_size: int = 10,
    ) -> List[NewsArticle]:
        """Get top headlines."""
        try:
            response = self.client.get_top_headlines(
                category=category,
                country=country,
                page_size=page_size,
            )
            return convert_api_response_to_articles(response)
        except Exception as e:
            raise NewsServiceError(f"Error fetching news: {str(e)}")

    async def __aenter__(self) -> "NewsService":
        """Enter async context."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context."""
        pass  # No need to close anything with the NewsApiClient
