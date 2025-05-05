"""News endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.schemas import NewsArticle, NewsSearchParams
from app.services.auth import get_current_user
from app.services.news import NewsService
from app.db.models import User
from fastapi import Query

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/search", response_model=List[NewsArticle])
async def search_news(
    query: str | None = None,
    category: str | None = None,
    language: str = "en",
    page_size: int = 10,
    page: int = 1,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> List[NewsArticle]:
    """Search for news articles.

    Args:
        query: Search query.
        category: News category.
        language: Language code.
        page_size: Number of articles per page.
        page: Page number.
        current_user: Current authenticated user.
        session: Database session.

    Returns:
        List[NewsArticle]: List of news articles.
    """
    try:
        params = NewsSearchParams(
            query=query,
            category=category,
            language=language,
            page_size=page_size,
            page=page,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors() if hasattr(e, 'errors') else str(e),
        )

    try:
        async with NewsService() as news_service:
            articles = await news_service.search_articles(params)
            return articles
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/headlines", response_model=List[NewsArticle])
async def get_headlines(
    category: str | None = None,
    country: str = "us",
    page_size: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> List[NewsArticle]:
    """Get top headlines.

    Args:
        category: News category.
        country: Country code.
        page_size: Number of articles to return.
        current_user: Current authenticated user.
        session: Database session.

    Returns:
        List[NewsArticle]: List of news articles.
    """
    try:
        async with NewsService() as news_service:
            articles = await news_service.get_top_headlines(
                category=category,
                country=country,
                page_size=page_size,
            )
            return articles
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
