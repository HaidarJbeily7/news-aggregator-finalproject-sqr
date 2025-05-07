import pytest
from httpx import AsyncClient
from app.main import app
from app.db.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch
from datetime import datetime


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_user(db: AsyncSession):
    user = User(
        email="test@example.com",
        firebase_uid="test_firebase_uid",
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
def mock_firebase_token():
    """Mock Firebase token verification."""
    with patch('firebase_admin.auth.verify_id_token') as mock_verify:
        mock_verify.return_value = {"uid": "test_firebase_uid"}
        yield "mock_firebase_token"


@pytest.mark.asyncio
async def test_complete_user_journey(async_client, mock_firebase_token):
    headers = {"Authorization": f"Bearer {mock_firebase_token}"}

    # 1. Register a new user
    register_data = {
        "email": "journey_test@example.com",
        "firebase_uid": "test_firebase_uid"
    }
    response = await async_client.post(
        "/api/v1/register",
        json=register_data,
        headers=headers
    )
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == register_data["email"]
    assert "id" in user_data

    # 2. Get current user info
    response = await async_client.get("/api/v1/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == register_data["email"]

    # 3. Search for news
    response = await async_client.get(
        "/api/v1/news/search",
        headers=headers,
        params={"query": "technology", "language": "en", "page_size": 5}
    )
    assert response.status_code == 200
    news_data = response.json()
    assert isinstance(news_data, list)
    if len(news_data) > 0:
        article = news_data[0]
        assert "title" in article
        assert "description" in article
        assert "url" in article
        assert "source" in article

    # 4. Get headlines
    response = await async_client.get(
        "/api/v1/news/headlines",
        headers=headers,
        params={"country": "us", "page_size": 5}
    )
    assert response.status_code == 200
    headlines = response.json()
    assert isinstance(headlines, list)
    if len(headlines) > 0:
        article = headlines[0]
        assert "title" in article
        assert "description" in article
        assert "url" in article
        assert "source" in article

    # 5. Create a bookmark
    if len(news_data) > 0:
        article = news_data[0]
        # Convert published_at string to datetime if it exists
        published_at = None
        if article.get("published_at"):
            try:
                published_at = datetime.fromisoformat(
                    article["published_at"].replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                pass

        bookmark_data = {
            "article_id": article["id"] or str(hash(article["url"])),
            "title": article["title"],
            "description": article.get("description", ""),
            "url": article["url"],
            "source": article["source"],
            "published_at": published_at.isoformat() if published_at else None
        }
        response = await async_client.post(
            "/api/v1/bookmarks",
            headers=headers,
            json=bookmark_data
        )
        assert response.status_code == 201
        bookmark = response.json()
        assert bookmark["title"] == article["title"]
        bookmark_id = bookmark["id"]

        # 6. Get all bookmarks
        response = await async_client.get("/api/v1/bookmarks", headers=headers)
        assert response.status_code == 200
        bookmarks = response.json()
        assert isinstance(bookmarks, list)
        assert any(b["id"] == bookmark_id for b in bookmarks)

        # 7. Delete bookmark
        response = await async_client.delete(
            f"/api/v1/bookmarks/{bookmark_id}",
            headers=headers
        )
        assert response.status_code == 204

        # Verify bookmark was deleted
        response = await async_client.get("/api/v1/bookmarks", headers=headers)
        assert response.status_code == 200
        bookmarks = response.json()
        assert not any(b["id"] == bookmark_id for b in bookmarks)
