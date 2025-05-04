"""Authentication endpoints for user management."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import User
from app.db.session import get_session
from app.models.schemas import UserCreate, User as UserSchema
from app.services.auth import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserSchema,
             status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> User:
    """Register a new user.

    Args:
        user_data: User creation data.
        session: Database session.

    Returns:
        User: The created user.

    Raises:
        HTTPException: If the user already exists.
    """
    # Check if user already exists
    result = await session.execute(
        select(User).where(User.firebase_uid == user_data.firebase_uid)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    # Create new user
    user = User(
        firebase_uid=user_data.firebase_uid,
        email=user_data.email,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current user information.

    Args:
        current_user: The current authenticated user.

    Returns:
        User: The current user.
    """
    return current_user
