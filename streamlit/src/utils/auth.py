"""Authentication utilities for the Streamlit app."""
import streamlit as st
from typing import Dict, Any, Optional
import httpx
from .config import API_BASE_URL


class ApiError(Exception):
    """Base exception for API-related errors."""
    pass


class AuthenticationError(ApiError):
    """Exception raised when authentication is required or fails."""
    pass


def init_auth_state():
    """Initialize authentication state in session state."""
    if "auth_state" not in st.session_state:
        st.session_state["auth_state"] = {
            "is_authenticated": False,
            "user": None,
            "token": None
        }


def set_auth_state(user: Dict[str, Any], token: str):
    """Set authentication state in session state.

    Args:
        user: User data from Firebase
        token: Firebase ID token
    """
    st.session_state["auth_state"] = {
        "is_authenticated": True,
        "user": user,
        "token": token
    }


def clear_auth_state():
    """Clear authentication state from session state."""
    st.session_state["auth_state"] = {
        "is_authenticated": False,
        "user": None,
        "token": None
    }


def get_auth_state() -> Dict[str, Any]:
    """Get current authentication state.

    Returns:
        Dict[str, Any]: Current authentication state
    """
    return st.session_state.get("auth_state", {
        "is_authenticated": False,
        "user": None,
        "token": None
    })


def get_auth_token() -> Optional[str]:
    """Get current authentication token.

    Returns:
        Optional[str]: Authentication token if authenticated, None otherwise
    """
    return get_auth_state()["token"]


def is_authenticated() -> bool:
    """Check if user is authenticated.

    Returns:
        bool: True if user is authenticated, False otherwise
    """
    return get_auth_state()["is_authenticated"]


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get current authenticated user.

    Returns:
        Optional[Dict[str, Any]]: User data if authenticated, None otherwise
    """
    return get_auth_state()["user"]


async def fetch_user_info(token: str) -> Dict[str, Any]:
    """Fetch user information from the backend API.

    Args:
        token: Firebase ID token

    Returns:
        Dict[str, Any]: User information from backend

    Raises:
        Exception: If request fails
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE_URL}/api/v1/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise AuthenticationError(f"Failed to fetch user info: {str(e)}")


def require_auth():
    """Decorator to require authentication for Streamlit pages.

    Raises:
        Exception: If user is not authenticated
    """
    if not is_authenticated():
        st.error("Please log in to access this page.")
        st.stop()
