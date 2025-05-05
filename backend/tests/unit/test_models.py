"""Tests for database models and Pydantic schemas."""
import pytest
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, Bookmark
from app.models.schemas import (
    UserBase,
    UserCreate,
    User as UserSchema,
    BookmarkBase,
    BookmarkCreate,
    Bookmark as BookmarkSchema,
    NewsArticle,
    NewsSearchParams,
)


@pytest.mark.asyncio
async def test_bookmark_model(session: AsyncSession):
    """Test Bookmark model creation and relationships."""
    user = User(email="test@example.com", firebase_uid="test-uid")
    session.add(user)
    await session.commit()

    bookmark = Bookmark(
        user_id=user.id,
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

    assert bookmark.title == "Test Article"
    assert bookmark.user_id == user.id
    assert bookmark.user == user
    assert isinstance(bookmark.created_at, datetime)
    assert isinstance(bookmark.updated_at, datetime)


def test_user_schemas():
    """Test User Pydantic schemas."""
    # Test UserBase
    user_base = UserBase(email="test@example.com", firebase_uid="test-uid")
    assert user_base.email == "test@example.com"
    assert user_base.firebase_uid == "test-uid"

    # Test UserCreate
    user_create = UserCreate(email="test@example.com", firebase_uid="test-uid")
    assert user_create.email == "test@example.com"
    assert user_create.firebase_uid == "test-uid"

    # Test User (response model)
    user = UserSchema(
        id=1,
        email="test@example.com",
        firebase_uid="test-uid",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.firebase_uid == "test-uid"


def test_bookmark_schemas():
    """Test Bookmark Pydantic schemas."""
    # Test BookmarkBase
    bookmark_base = BookmarkBase(
        article_id="test-article",
        title="Test Article",
        description="Test Description",
        url="https://example.com/test",
        source="Test Source",
        published_at=datetime.now(UTC),
    )
    assert bookmark_base.title == "Test Article"
    assert bookmark_base.article_id == "test-article"

    # Test BookmarkCreate
    bookmark_create = BookmarkCreate(
        article_id="test-article",
        title="Test Article",
        description="Test Description",
        url="https://example.com/test",
        source="Test Source",
        published_at=datetime.now(UTC),
    )
    assert bookmark_create.title == "Test Article"
    assert bookmark_create.article_id == "test-article"

    # Test Bookmark (response model)
    bookmark_schema = BookmarkSchema(
        id=1,
        user_id=1,
        article_id="test-article",
        title="Test Article",
        description="Test Description",
        url="https://example.com/test",
        source="Test Source",
        published_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    assert bookmark_schema.id == 1
    assert bookmark_schema.user_id == 1
    assert bookmark_schema.title == "Test Article"


def test_news_schemas():
    """Test News Pydantic schemas."""
    # Test NewsArticle
    article = NewsArticle(
        title="Test Article",
        description="Test Description",
        url="https://example.com/test",
        source="Test Source",
        published_at=datetime.now(UTC),
        category="technology",
        author="Test Author",
        image_url="https://example.com/image.jpg",
    )
    assert article.title == "Test Article"
    assert article.source == "Test Source"
    assert article.category == "technology"

    # Test NewsSearchParams
    params = NewsSearchParams(
        query="test query",
        category="technology",
        language="en",
        page_size=10,
        page=1,
    )
    assert params.query == "test query"
    assert params.category == "technology"
    assert params.language == "en"
    assert params.page_size == 10
    assert params.page == 1

    # Test validation
    with pytest.raises(ValueError):
        NewsSearchParams(page_size=0)  # Should fail validation

    with pytest.raises(ValueError):
        NewsSearchParams(page=0)  # Should fail validation
    with pytest.raises(ValueError):
        NewsSearchParams(page=0)  # Should fail validation
