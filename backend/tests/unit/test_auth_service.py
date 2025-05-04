"""Tests for the auth service."""
import pytest
from unittest.mock import patch
from firebase_admin import auth
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.services.auth import get_current_user
from app.db.models import User


@pytest.fixture
def mock_firebase_user():
    """Fixture for mock Firebase user."""
    return {
        "email": "test@example.com",
        "uid": "test-uid",
    }


@pytest.fixture
async def mock_db_user(session):
    """Fixture for mock database user."""
    user = User(
        firebase_uid="test-uid",
        email="test@example.com",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.fixture
def mock_credentials():
    """Fixture for mock HTTP authorization credentials."""
    return HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="valid-token")


@pytest.mark.asyncio
async def test_get_current_user(
        mock_firebase_user,
        mock_db_user,
        mock_credentials,
        session):
    """Test getting current user with valid token."""
    with patch(
        "firebase_admin.auth.verify_id_token",
        return_value=mock_firebase_user
    ):
        user = await get_current_user(mock_credentials, session)
        assert user.email == "test@example.com"
        assert user.firebase_uid == "test-uid"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_credentials, session):
    """Test getting current user with invalid token."""
    with patch("firebase_admin.auth.verify_id_token",
               side_effect=auth.InvalidIdTokenError("Invalid token", None)):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials, session)
        assert exc_info.value.status_code == 401
        assert "Invalid authentication token" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_expired_token(mock_credentials, session):
    """Test getting current user with expired token."""
    with patch("firebase_admin.auth.verify_id_token",
               side_effect=auth.ExpiredIdTokenError("Expired token", None)):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials, session)
        assert exc_info.value.status_code == 401
        assert "Expired authentication token" in exc_info.value.detail
