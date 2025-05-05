"""Firebase authentication service."""

import firebase_admin
from firebase_admin import auth
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.core.config import settings
from app.db.models import User
from app.db.session import get_session
from app.core.error import handle_auth_error
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.firebase import initialize_firebase

security = HTTPBearer()
cred = initialize_firebase()
if cred and not settings.TESTING:
    # Initialize Firebase app if not already initialized
    try:
        firebase_admin.initialize_app(cred)
    except ValueError:
        # App already exists, get the default app
        firebase_admin.get_app()


class AuthService:
    """Service for handling authentication."""

    def __init__(self, session: AsyncSession):
        """Initialize the AuthService."""
        self.session = session

    async def get_current_user(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = None,
    ) -> User:
        """Get the current authenticated user."""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication credentials not provided",
            )

        try:
            return await self._verify_and_get_user(credentials.credentials)
        except Exception as e:
            handle_auth_error(e)

    async def _verify_and_get_user(self, token: str) -> User:
        """Verify token and retrieve user from database."""
        firebase_uid = self._verify_token(token)
        return await self._get_user_by_firebase_uid(firebase_uid)

    def _verify_token(self, token: str) -> str:
        """Verify Firebase ID token and return user ID."""
        decoded_token = auth.verify_id_token(token)
        return decoded_token["uid"]

    async def _get_user_by_firebase_uid(self, firebase_uid: str) -> User:
        """Get user from database by Firebase UID."""
        user = await self._find_user_by_firebase_uid(firebase_uid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return user

    async def _find_user_by_firebase_uid(
            self, firebase_uid: str) -> Optional[User]:
        """Find user in database by Firebase UID."""
        result = await self.session.execute(
            select(User).where(User.firebase_uid == firebase_uid)
        )
        return result.scalar_one_or_none()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Get the current authenticated user."""
    auth_service = AuthService(session)
    return await auth_service.get_current_user(credentials)
