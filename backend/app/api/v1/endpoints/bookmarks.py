"""Bookmark endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Bookmark, User
from app.db.session import get_session
from app.models.schemas import Bookmark as BookmarkSchema, BookmarkCreate
from app.services.auth import get_current_user


router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


@router.post("", response_model=BookmarkSchema,
             status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    bookmark_data: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Bookmark:
    """Create a new bookmark.

    Args:
        bookmark_data: Bookmark data.
        current_user: Current authenticated user.
        session: Database session.

    Returns:
        Bookmark: Created bookmark.

    Raises:
        HTTPException: If the bookmark already exists.
    """
    await _check_bookmark_exists(
        session,
        current_user.id,
        bookmark_data.article_id,
    )

    # Create new bookmark
    bookmark = Bookmark(
        user_id=current_user.id,
        article_id=bookmark_data.article_id,
        title=bookmark_data.title,
        description=bookmark_data.description,
        url=bookmark_data.url,
        source=bookmark_data.source,
        published_at=bookmark_data.published_at,
    )
    session.add(bookmark)
    await session.commit()
    await session.refresh(bookmark)

    return bookmark


async def _check_bookmark_exists(
    session: AsyncSession, user_id: int, article_id: str
) -> None:
    """Check if a bookmark already exists for the user.

    Args:
        session: Database session.
        user_id: User ID.
        article_id: Article ID.

    Raises:
        HTTPException: If the bookmark already exists.
    """
    existing_bookmark = await session.execute(
        select(Bookmark).where(
            Bookmark.user_id == user_id,
            Bookmark.article_id == article_id,
        )
    )
    if existing_bookmark.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bookmark already exists",
        )


@router.get("", response_model=List[BookmarkSchema])
async def get_bookmarks(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> List[Bookmark]:
    """Get all bookmarks for the current user.

    Args:
        current_user: Current authenticated user.
        session: Database session.

    Returns:
        list[Bookmark]: List of bookmarks.
    """
    result = await session.execute(
        select(Bookmark).where(Bookmark.user_id == current_user.id)
    )
    return result.scalars().all()


@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    bookmark_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a bookmark.

    Args:
        bookmark_id: ID of the bookmark to delete.
        current_user: Current authenticated user.
        session: Database session.

    Raises:
        HTTPException: If the bookmark is not found or
        does not belong to the user.
    """
    bookmark = await _get_user_bookmark(session, bookmark_id, current_user.id)
    await session.delete(bookmark)
    await session.commit()


async def _get_user_bookmark(
    session: AsyncSession, bookmark_id: int, user_id: int
) -> Bookmark:
    """Get a bookmark that belongs to the user.

    Args:
        session: Database session.
        bookmark_id: Bookmark ID.
        user_id: User ID.

    Returns:
        Bookmark: The bookmark.

    Raises:
        HTTPException: If bookmark is not found or does not belong to the user.
    """
    bookmark = await session.get(Bookmark, bookmark_id)
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )

    if bookmark.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this bookmark",
        )

    return bookmark
