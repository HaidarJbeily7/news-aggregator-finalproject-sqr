"""Tests for bookmark endpoints."""
import pytest
from datetime import datetime, UTC
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, AsyncMock

from app.api.v1.api import api_router
from app.db.models import User, Bookmark
from app.services.auth import AuthService


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
    user = User(
        email="test@example.com",
        firebase_uid="test-uid",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.fixture
def mock_auth_service(test_user: User):
    """Create a mock for AuthService."""
    async def get_current_user_override(credentials=None):
        return test_user

    mock_service = AsyncMock(spec=AuthService)
    mock_service.get_current_user.side_effect = get_current_user_override

    # Create a patch for the dependency
    with patch("app.services.auth.AuthService", return_value=mock_service):
        yield mock_service


@pytest.fixture
async def test_bookmark(session: AsyncSession, test_user: User) -> Bookmark:
    """Create a test bookmark."""
    bookmark = Bookmark(
        user_id=test_user.id,
        article_id="test-article",
        title="Test Article",
        description="Test Description",
        url="https://example.com/test",
        source="Test Source",
        published_at=datetime.now(UTC),
    )
    session.add(bookmark)
    await session.commit()
    await session.refresh(bookmark)
    return bookmark


@pytest.fixture
def test_bookmark_data() -> dict:
    """Create test bookmark data."""
    return {
        "title": "Test Article",
        "description": "Test Description",
        "url": "https://example.com/test-article",
        "source": "Test Source",
        "article_id": "test-article-id",
        "published_at": datetime.now(UTC).isoformat(),
    }


@pytest.mark.asyncio
async def test_create_bookmark(
        client: AsyncClient,
        test_bookmark_data: dict,
        mock_auth_service):
    """Test creating a bookmark."""
    response = await client.post(
        "/api/v1/bookmarks",
        json=test_bookmark_data,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == test_bookmark_data["title"]
    assert data["description"] == test_bookmark_data["description"]
    assert data["source"] == test_bookmark_data["source"]


@pytest.mark.asyncio
async def test_get_bookmarks(
        client: AsyncClient,
        test_bookmark_data: dict,
        mock_auth_service):
    """Test getting bookmarks."""
    # First create a bookmark
    await client.post("/api/v1/bookmarks", json=test_bookmark_data)

    # Then get all bookmarks
    response = await client.get("/api/v1/bookmarks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["title"] == test_bookmark_data["title"]


@pytest.mark.asyncio
async def test_delete_bookmark(
        client: AsyncClient,
        test_bookmark_data: dict,
        mock_auth_service):
    """Test deleting a bookmark."""
    # First create a bookmark
    create_response = await client.post(
        "/api/v1/bookmarks",
        json=test_bookmark_data
    )
    bookmark_id = create_response.json()["id"]

    # Then delete it
    response = await client.delete(f"/api/v1/bookmarks/{bookmark_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_nonexistent_bookmark(
        client: AsyncClient,
        mock_auth_service):
    """Test deleting a nonexistent bookmark."""
    response = await client.delete("/api/v1/bookmarks/999")
    assert response.status_code == 404
