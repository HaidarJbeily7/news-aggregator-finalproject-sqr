import pytest
import streamlit as st
from unittest.mock import AsyncMock, patch
from src.pages.bookmarks import remove_bookmark, load_bookmarks, main


class MockContainer:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture(autouse=True)
def mock_streamlit(monkeypatch):
    """Mock Streamlit functions for testing."""
    def mock_title(text):
        return text

    def mock_success(text):
        return text

    def mock_error(text):
        return text

    def mock_info(text):
        return text

    def mock_rerun():
        return None

    def mock_container():
        return MockContainer()

    monkeypatch.setattr(st, "title", mock_title)
    monkeypatch.setattr(st, "success", mock_success)
    monkeypatch.setattr(st, "error", mock_error)
    monkeypatch.setattr(st, "info", mock_info)
    monkeypatch.setattr(st, "rerun", mock_rerun)
    monkeypatch.setattr(st, "container", mock_container)


@pytest.fixture
def mock_session_state(monkeypatch):
    """Mock Streamlit's session state for testing."""
    session_state = {}
    monkeypatch.setattr(st, "session_state", session_state)
    return session_state


@pytest.mark.asyncio
async def test_remove_bookmark_success(mock_session_state):
    """Test successful bookmark removal."""
    bookmark_id = 123
    mock_session_state["bookmark_removed"] = False

    with patch(
        "src.pages.bookmarks.delete_bookmark",
        new_callable=AsyncMock
    ) as mock_delete:
        await remove_bookmark(bookmark_id)
        mock_delete.assert_called_once_with(bookmark_id)
        assert mock_session_state["bookmark_removed"] is True


@pytest.mark.asyncio
async def test_remove_bookmark_failure(mock_session_state):
    """Test failed bookmark removal."""
    bookmark_id = 123
    mock_session_state["bookmark_removed"] = False

    with patch(
        "src.pages.bookmarks.delete_bookmark",
        new_callable=AsyncMock
    ) as mock_delete:
        mock_delete.side_effect = Exception("Network error")
        await remove_bookmark(bookmark_id)
        mock_delete.assert_called_once_with(bookmark_id)
        # Should remain False on failure
        assert mock_session_state["bookmark_removed"] is False


@pytest.mark.asyncio
async def test_load_bookmarks_with_bookmarks(mock_session_state):
    """Test loading bookmarks with data."""
    mock_bookmarks = [
        {
            "id": 1,
            "title": "Test Article 1",
            "description": "Test description 1",
            "url": "https://example.com/1",
            "source": "Test Source 1",
            "published_at": "2024-03-15T12:00:00Z"
        },
        {
            "id": 2,
            "title": "Test Article 2",
            "description": "Test description 2",
            "url": "https://example.com/2",
            "source": "Test Source 2",
            "published_at": "2024-03-15T12:00:00Z"
        }
    ]

    with patch(
        "src.pages.bookmarks.get_bookmarks",
        new_callable=AsyncMock
    ) as mock_get_bookmarks:
        mock_get_bookmarks.return_value = mock_bookmarks
        await load_bookmarks()
        mock_get_bookmarks.assert_called_once()


@pytest.mark.asyncio
async def test_load_bookmarks_no_bookmarks(mock_session_state):
    """Test loading bookmarks with no data."""
    with patch(
        "src.pages.bookmarks.get_bookmarks",
        new_callable=AsyncMock
    ) as mock_get_bookmarks:
        mock_get_bookmarks.return_value = []
        await load_bookmarks()
        mock_get_bookmarks.assert_called_once()


@pytest.mark.asyncio
async def test_load_bookmarks_error(mock_session_state):
    """Test loading bookmarks with error."""
    with patch(
        "src.pages.bookmarks.get_bookmarks",
        new_callable=AsyncMock
    ) as mock_get_bookmarks:
        mock_get_bookmarks.side_effect = Exception("API error")
        await load_bookmarks()
        mock_get_bookmarks.assert_called_once()


def test_main_with_bookmark_removed(mock_session_state):
    """Test main function with bookmark removal."""
    mock_session_state["bookmark_removed"] = True

    with patch(
        "src.pages.bookmarks.load_bookmarks",
        new_callable=AsyncMock
    ) as mock_load_bookmarks:
        main()
        mock_load_bookmarks.assert_called_once()
        assert "bookmark_removed" not in mock_session_state


def test_main_without_bookmark_removed(mock_session_state):
    """Test main function without bookmark removal."""
    with patch(
        "src.pages.bookmarks.load_bookmarks",
        new_callable=AsyncMock
    ) as mock_load_bookmarks:
        main()
        mock_load_bookmarks.assert_called_once()
        assert "bookmark_removed" not in mock_session_state
