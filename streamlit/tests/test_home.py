import pytest
import streamlit as st
from unittest.mock import AsyncMock, patch
from src.home import handle_user_auth, load_headlines, main


class MockContainer:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class MockTab(MockContainer):
    pass


class MockSpinner(MockContainer):
    pass


@pytest.fixture(autouse=True)
def mock_streamlit(monkeypatch):
    """Mock Streamlit functions for testing."""
    def mock_title(text):
        return text

    def mock_write(text):
        return text

    def mock_success(text):
        return text

    def mock_error(text):
        return text

    def mock_info(text):
        return text

    def mock_spinner(text):
        return MockSpinner()

    def mock_button(text, on_click=None, use_container_width=False):
        return None

    def mock_rerun():
        return None

    def mock_text_input(label, key=None, type=None):
        return "test@example.com"

    def mock_tabs(tab_names):
        return [MockTab(), MockTab()]

    def mock_subheader(text):
        return text

    def mock_columns(ratio):
        return [MockContainer(), MockContainer()]

    monkeypatch.setattr(st, "title", mock_title)
    monkeypatch.setattr(st, "write", mock_write)
    monkeypatch.setattr(st, "success", mock_success)
    monkeypatch.setattr(st, "error", mock_error)
    monkeypatch.setattr(st, "info", mock_info)
    monkeypatch.setattr(st, "spinner", mock_spinner)
    monkeypatch.setattr(st, "button", mock_button)
    monkeypatch.setattr(st, "rerun", mock_rerun)
    monkeypatch.setattr(st, "text_input", mock_text_input)
    monkeypatch.setattr(st, "tabs", mock_tabs)
    monkeypatch.setattr(st, "subheader", mock_subheader)
    monkeypatch.setattr(st, "columns", mock_columns)


@pytest.fixture
def mock_session_state(monkeypatch):
    """Mock Streamlit's session state for testing."""
    session_state = {}
    monkeypatch.setattr(st, "session_state", session_state)
    return session_state


@pytest.mark.asyncio
async def test_handle_user_auth_successful_login():
    """Test successful user login."""
    firebase_user = {
        "email": "test@example.com",
        "uid": "123",
        "idToken": "test_token"
    }

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"token": "test_token"}

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response  # noqa: E501
        token = await handle_user_auth(firebase_user)
        assert token == "test_token"


@pytest.mark.asyncio
async def test_handle_user_auth_successful_register():
    """Test successful user registration."""
    firebase_user = {
        "email": "test@example.com",
        "uid": "123",
        "idToken": "test_token"
    }

    # Mock failed login
    mock_login_response = AsyncMock()
    mock_login_response.status_code = 404

    # Mock successful registration
    mock_register_response = AsyncMock()
    mock_register_response.status_code = 201
    mock_register_response.json.return_value = {"token": "test_token"}

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_login_response  # noqa: E501
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_register_response  # noqa: E501
        token = await handle_user_auth(firebase_user)
        assert token == "test_token"


@pytest.mark.asyncio
async def test_handle_user_auth_failure():
    """Test authentication failure."""
    firebase_user = {
        "email": "test@example.com",
        "uid": "123",
        "idToken": "test_token"
    }

    # Mock failed login and registration
    mock_login_response = AsyncMock()
    mock_login_response.status_code = 404

    mock_register_response = AsyncMock()
    mock_register_response.status_code = 400
    mock_register_response.text = "Registration failed"

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_login_response  # noqa: E501
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_register_response  # noqa: E501
        with pytest.raises(Exception) as exc_info:
            await handle_user_auth(firebase_user)
        assert "Failed to authenticate user" in str(exc_info.value)


@pytest.mark.asyncio
async def test_load_headlines_with_headlines(mock_session_state):
    """Test loading headlines with data."""
    mock_session_state["selected_category"] = "all"
    mock_headlines = [
        {
            "title": "Test Headline 1",
            "url": "https://example.com/1",
            "source": "Test Source"
        },
        {
            "title": "Test Headline 2",
            "url": "https://example.com/2",
            "source": "Test Source"
        }
    ]

    with patch(
        "src.home.get_headlines",
        new_callable=AsyncMock
    ) as mock_get_headlines:
        mock_get_headlines.return_value = mock_headlines
        await load_headlines()
        mock_get_headlines.assert_called_once_with("all")


@pytest.mark.asyncio
async def test_load_headlines_no_headlines(mock_session_state):
    """Test loading headlines with no data."""
    mock_session_state["selected_category"] = "all"

    with patch(
        "src.home.get_headlines",
        new_callable=AsyncMock
    ) as mock_get_headlines:
        mock_get_headlines.return_value = []
        await load_headlines()
        mock_get_headlines.assert_called_once_with("all")


def test_main_authenticated(mock_session_state):
    """Test main function when user is authenticated."""
    mock_session_state["auth_state"] = {
        "is_authenticated": True,
        "user": {"email": "test@example.com"},
        "token": "test_token"
    }

    with patch("src.utils.firebase.firebase_logout") as mock_logout:
        main()
        mock_logout.assert_not_called()
