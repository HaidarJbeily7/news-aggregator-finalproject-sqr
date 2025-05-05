"""Firebase authentication utilities for the Streamlit app."""
import streamlit as st
import requests
from typing import Dict, Any, Optional

from .config import (
    FIREBASE_API_KEY,
    FIREBASE_AUTH_DOMAIN,
    FIREBASE_PROJECT_ID,
    FIREBASE_STORAGE_BUCKET,
    FIREBASE_MESSAGING_SENDER_ID,
    FIREBASE_APP_ID
)
from .auth import set_auth_state, clear_auth_state


def get_firebase_config() -> Dict[str, str]:
    """Get Firebase configuration.

    Returns:
        Dict[str, str]: Firebase configuration.
    """
    return {
        "apiKey": FIREBASE_API_KEY,
        "authDomain": FIREBASE_AUTH_DOMAIN,
        "projectId": FIREBASE_PROJECT_ID,
        "storageBucket": FIREBASE_STORAGE_BUCKET,
        "messagingSenderId": FIREBASE_MESSAGING_SENDER_ID,
        "appId": FIREBASE_APP_ID
    }


def check_firebase_config() -> bool:
    """Check if Firebase configuration is complete.

    Returns:
        bool: True if configuration is complete, False otherwise
    """
    return all([
        FIREBASE_API_KEY,
        FIREBASE_AUTH_DOMAIN,
        FIREBASE_PROJECT_ID,
        FIREBASE_STORAGE_BUCKET,
        FIREBASE_MESSAGING_SENDER_ID,
        FIREBASE_APP_ID
    ])


def firebase_login_ui() -> Optional[Dict[str, Any]]:
    """Display Firebase login UI using native Streamlit components.

    Returns:
        Optional[Dict[str, Any]]: Firebase user data if login successful,
            None otherwise.
    """
    if not check_firebase_config():
        st.error(
            "Firebase configuration is incomplete. "
            "Please check your .env file."
        )
        return None

    # Create tabs for login options
    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    with login_tab:
        st.subheader("Login to your account")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input(
            "Password", type="password", key="login_password")
        login_col1, login_col2 = st.columns([1, 3])
        with login_col1:
            login_button = st.button("Login", use_container_width=True)
        if login_button and login_email and login_password:
            try:
                # Use Firebase REST API for email/password login
                response = requests.post(
                    f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}",  # noqa: E501
                    json={
                        "email": login_email,
                        "password": login_password,
                        "returnSecureToken": True})

                if response.status_code == 200:
                    user_data = response.json()
                    # Format user data to match our expected structure
                    formatted_user = {
                        "displayName": user_data.get("displayName", ""),
                        "email": user_data["email"],
                        "uid": user_data["localId"],
                        "idToken": user_data["idToken"],
                        "photoURL": user_data.get("photoUrl", "")
                    }
                    set_auth_state(formatted_user, user_data["idToken"])
                    return formatted_user
                else:
                    error_data = response.json()
                    error_message = error_data.get(
                        "error", {}).get(
                        "message", "Unknown error")
                    if error_message == "EMAIL_NOT_FOUND" or error_message == "INVALID_PASSWORD":    # noqa: E501
                        st.error("Invalid email or password")
                    else:
                        st.error(f"Login failed: {error_message}")
            except Exception as e:
                st.error(f"Login failed: {str(e)}")

    with signup_tab:
        st.subheader("Create a new account")
        signup_name = st.text_input("Full Name", key="signup_name")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input(
            "Password", type="password", key="signup_password")
        signup_confirm = st.text_input(
            "Confirm Password",
            type="password",
            key="signup_confirm")

        signup_col1, signup_col2 = st.columns([1, 3])
        with signup_col1:
            signup_button = st.button("Sign Up", use_container_width=True)

        if signup_button:
            if not signup_name:
                st.error("Please enter your name")
            elif not signup_email:
                st.error("Please enter your email")
            elif not signup_password:
                st.error("Please enter a password")
            elif signup_password != signup_confirm:
                st.error("Passwords do not match")
            else:
                try:
                    # Use Firebase REST API for email/password signup
                    response = requests.post(
                        f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}",  # noqa: E501
                        json={
                            "email": signup_email,
                            "password": signup_password,
                            "returnSecureToken": True})

                    if response.status_code == 200:
                        user_data = response.json()

                        # Update profile to add display name
                        profile_response = requests.post(
                            f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={FIREBASE_API_KEY}",  # noqa: E501
                            json={
                                "idToken": user_data["idToken"],
                                "displayName": signup_name,
                                "returnSecureToken": True})

                        if profile_response.status_code == 200:
                            updated_data = profile_response.json()
                            # Format user data to match our expected structure
                            formatted_user = {
                                "displayName": signup_name,
                                "email": user_data["email"],
                                "uid": user_data["localId"],
                                "idToken": updated_data.get(
                                    "idToken",
                                    user_data["idToken"]),
                                "photoURL": ""}
                            set_auth_state(
                                formatted_user, formatted_user["idToken"])
                            st.success("Account created successfully!")
                            return formatted_user
                        else:
                            error_data = profile_response.json()
                            st.error(
                                f"Failed to update profile: {
                                    error_data.get(
                                        'error', {}).get(
                                        'message', 'Unknown error')}")
                    else:
                        error_data = response.json()
                        error_message = error_data.get(
                            "error", {}).get(
                            "message", "Unknown error")
                        if error_message == "EMAIL_EXISTS":
                            st.error(
                                "Email already in use. Please use a different email or try logging in.")  # noqa: E501
                        else:
                            st.error(f"Sign up failed: {error_message}")
                except Exception as e:
                    st.error(f"Sign up failed: {str(e)}")

    return None


def firebase_logout():
    """Logout from Firebase and clear auth state."""
    # Firebase REST API doesn't have a logout endpoint
    # We just need to clear the local auth state
    clear_auth_state()
    st.success("Logged out successfully!")
    st.rerun()
