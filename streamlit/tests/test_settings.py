import pytest
import streamlit as st
from unittest.mock import patch
from src.pages.settings import main


@pytest.fixture(autouse=True)
def mock_streamlit(monkeypatch):
    """Mock Streamlit functions for testing."""
    def mock_title(text):
        return text

    def mock_write(text):
        return text

    def mock_error(text):
        return text

    def mock_info(text):
        return text

    def mock_divider():
        return None

    monkeypatch.setattr(st, "title", mock_title)
    monkeypatch.setattr(st, "write", mock_write)
    monkeypatch.setattr(st, "error", mock_error)
    monkeypatch.setattr(st, "info", mock_info)
    monkeypatch.setattr(st, "divider", mock_divider)


@pytest.fixture
def mock_session_state(monkeypatch):
    """Mock Streamlit's session state for testing."""
    session_state = {}
    monkeypatch.setattr(st, "session_state", session_state)
    return session_state


def test_main_with_user_info():
    """Test main function with user info."""
    user_info = {
        "email": "test@example.com",
        "displayName": "Test User"
    }

    with patch("src.pages.settings.get_current_user") as mock_get_user:
        mock_get_user.return_value = user_info
        main()
        mock_get_user.assert_called_once()


def test_main_without_user_info():
    """Test main function without user info."""
    with patch("src.pages.settings.get_current_user") as mock_get_user:
        mock_get_user.return_value = None
        main()
        mock_get_user.assert_called_once()
