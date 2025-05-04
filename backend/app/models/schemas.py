"""Pydantic models for request/response validation."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    firebase_uid: str


class UserCreate(UserBase):
    """User creation model."""
    pass


class User(UserBase):
    """User response model."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookmarkBase(BaseModel):
    """Base bookmark model."""
    article_id: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    url: str = Field(..., min_length=1, max_length=512)
    source: str = Field(..., min_length=1, max_length=255)
    published_at: Optional[datetime] = None


class BookmarkCreate(BookmarkBase):
    """Bookmark creation model."""
    pass


class Bookmark(BookmarkBase):
    """Bookmark response model."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NewsArticle(BaseModel):
    """News article model."""
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    url: str
    source: str
    published_at: Optional[datetime] = None
    category: Optional[str] = None
    author: Optional[str] = None
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class NewsSearchParams(BaseModel):
    """News search parameters model."""
    query: Optional[str] = None
    category: Optional[str] = None
    language: str = "en"
    page_size: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)
