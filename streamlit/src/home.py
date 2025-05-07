"""Main Streamlit application entry point."""
import streamlit as st
import httpx
import asyncio
from typing import Dict, Any

# Import components and utilities
from utils.firebase import firebase_login_ui, firebase_logout
from utils.auth import (
    init_auth_state,
    is_authenticated,
    fetch_user_info,
    clear_auth_state,
)
from utils.api import get_headlines
from components.article_card import article_card
from utils.config import API_BASE_URL
# Configure page settings
st.set_page_config(
    page_title="News Aggregator",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="auto",
)

# Initialize auth state
init_auth_state()


class AuthenticationError(Exception):
    """Custom exception for authentication failures."""
    pass


async def handle_user_auth(firebase_user: Dict[str, Any]) -> str:
    """Handle user authentication with the backend API.

    First tries to login, if that fails, registers the user.

    Args:
        firebase_user: Firebase user data.

    Returns:
        str: JWT token from backend.

    Raises:
        Exception: If both login and registration fail.
    """
    user_data = {
        "email": firebase_user["email"],
        "firebase_uid": firebase_user["uid"]
    }

    async with httpx.AsyncClient() as client:
        try:
            # First try to login
            response = await client.get(
                f"{API_BASE_URL}/api/v1/me",
                headers={"Authorization": f"Bearer {firebase_user['idToken']}"}
            )
            if response.status_code == 200:
                return firebase_user["idToken"]
            # If login fails, try to register
            response = await client.post(
                f"{API_BASE_URL}/api/v1/register",
                json=user_data
            )
            if response.status_code in (201, 200):
                return firebase_user["idToken"]
            else:
                error_msg = "Failed to authenticate user: " + response.text
                raise AuthenticationError(error_msg)
        except httpx.RequestError as e:
            raise AuthenticationError(
                f"Failed to connect to backend: {str(e)}")


async def load_headlines():
    """Load and display headlines."""
    category = st.session_state.get("selected_category", "all")
    headlines = await get_headlines(category)

    if headlines:
        for headline in headlines:
            article_card(headline)
    else:
        st.info("No headlines available for the selected category.")


def main():
    """Main application entry point."""
    st.title("Welcome to News Aggregator")
    st.write(
        "Please log in to access personalized news, "
        "search, and bookmarking features."
    )
    if is_authenticated():
        st.success("You are already logged in!")
        st.button("Logout", on_click=firebase_logout)
    else:
        # Display Firebase login UI
        firebase_user = firebase_login_ui()
        if firebase_user and "idToken" in firebase_user:
            with st.spinner("Logging in..."):
                try:
                    # Handle user authentication
                    token = asyncio.run(handle_user_auth(firebase_user))
                    # Fetch user info
                    asyncio.run(fetch_user_info(token))
                    st.success("Logged in successfully!")
                    st.rerun()
                except AuthenticationError as e:
                    clear_auth_state()
                    st.error(f"Login failed: {str(e)}")
                    st.info(
                        "Please try again or contact support "
                        "if the issue persists."
                    )


if __name__ == "__main__":
    main()
