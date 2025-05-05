"""API utilities for the Streamlit app."""
import httpx
from typing import Dict, List, Any, Optional

from .config import API_BASE_URL
from .auth import get_auth_token

AUTH_ERROR = "Authentication required"


class ApiError(Exception):
    """Base exception for API-related errors."""
    pass


class AuthenticationError(ApiError):
    """Exception raised when authentication is required or fails."""
    pass


class NewsApiError(ApiError):
    """Exception raised when news API requests fail."""
    pass


class BookmarkApiError(ApiError):
    """Exception raised when bookmark API requests fail."""
    pass


async def get_headlines(
    category: Optional[str] = None,
    country: str = "us",
    page_size: int = 10
) -> List[Dict[str, Any]]:
    """Get top headlines from the API.

    Args:
        category: News category.
        country: Country code.
        page_size: Number of articles to return.

    Returns:
        List[Dict[str, Any]]: List of news articles.

    Raises:
        Exception: If the request fails.
    """
    token = get_auth_token()
    if not token:
        raise AuthenticationError(AUTH_ERROR)

    params = {
        "country": country,
        "page_size": page_size
    }

    if category:
        params["category"] = category

    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/api/v1/news/headlines",
            headers=headers,
            params=params
        )

        if response.status_code == 200:
            return response.json()
        raise NewsApiError(f"Failed to fetch headlines: {response.text}")


async def search_news(
    query: Optional[str] = None,
    category: Optional[str] = None,
    language: str = "en",
    page_size: int = 10,
    page: int = 1
) -> List[Dict[str, Any]]:
    """Search for news articles.

    Args:
        query: Search query.
        category: News category.
        language: Language code.
        page_size: Number of articles per page.
        page: Page number.

    Returns:
        List[Dict[str, Any]]: List of news articles.

    Raises:
        Exception: If the request fails.
    """
    token = get_auth_token()
    if not token:
        raise AuthenticationError(AUTH_ERROR)

    params = {
        "language": language,
        "page_size": page_size,
        "page": page
    }

    if query:
        params["query"] = query

    if category:
        params["category"] = category

    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/api/v1/news/search",
            headers=headers,
            params=params
        )

        if response.status_code == 200:
            return response.json()
        raise NewsApiError(f"Failed to search news: {response.text}")


async def get_bookmarks() -> List[Dict[str, Any]]:
    """Get all bookmarks for the current user.

    Returns:
        List[Dict[str, Any]]: List of bookmarks.

    Raises:
        Exception: If the request fails.
    """
    token = get_auth_token()
    if not token:
        raise AuthenticationError(AUTH_ERROR)

    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/api/v1/bookmarks",
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        raise BookmarkApiError(f"Failed to fetch bookmarks: {response.text}")


async def create_bookmark(bookmark_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new bookmark.

    Args:
        bookmark_data: Bookmark data.

    Returns:
        Dict[str, Any]: Created bookmark.

    Raises:
        Exception: If the request fails.
    """
    token = get_auth_token()
    if not token:
        raise AuthenticationError(AUTH_ERROR)

    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/api/v1/bookmarks",
            headers=headers,
            json=bookmark_data
        )

        if response.status_code == 201:
            return response.json()
        raise Exception(f"Failed to create bookmark: {response.text}")


async def delete_bookmark(bookmark_id: int) -> None:
    """Delete a bookmark.

    Args:
        bookmark_id: ID of the bookmark to delete.

    Raises:
        Exception: If the request fails.
    """
    token = get_auth_token()
    if not token:
        raise AuthenticationError(AUTH_ERROR)

    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{API_BASE_URL}/api/v1/bookmarks/{bookmark_id}",
            headers=headers
        )

        if response.status_code != 204:
            raise Exception(f"Failed to delete bookmark: {response.text}")
