import pytest
import streamlit as st
from unittest.mock import AsyncMock, patch
from src.pages.search import bookmark_article, search_and_display, main


class MockContainer:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class MockForm(MockContainer):
    pass


def _mock_basic_functions(monkeypatch):
    """Mock basic Streamlit functions."""
    def mock_title(text):
        return text

    def mock_success(text):
        return text

    def mock_error(text):
        return text

    def mock_info(text):
        return text

    def mock_spinner(text):
        return MockContainer()

    monkeypatch.setattr(st, "title", mock_title)
    monkeypatch.setattr(st, "success", mock_success)
    monkeypatch.setattr(st, "error", mock_error)
    monkeypatch.setattr(st, "info", mock_info)
    monkeypatch.setattr(st, "spinner", mock_spinner)


def _mock_form_functions(monkeypatch):
    """Mock form-related Streamlit functions."""
    def mock_form(key):
        return MockForm()

    def mock_text_input(label, key=None, placeholder=None):
        return f"input_{label}"

    def mock_selectbox(label, options, format_func=None, key=None):
        return options[0] if options else None

    def mock_form_submit_button(label):
        return True

    monkeypatch.setattr(st, "form", mock_form)
    monkeypatch.setattr(st, "text_input", mock_text_input)
    monkeypatch.setattr(st, "selectbox", mock_selectbox)
    monkeypatch.setattr(st, "form_submit_button", mock_form_submit_button)


def _mock_layout_functions(monkeypatch):
    """Mock layout-related Streamlit functions."""
    def mock_columns(ratio):
        return [MockContainer() for _ in ratio]

    def mock_container():
        return MockContainer()

    monkeypatch.setattr(st, "columns", mock_columns)
    monkeypatch.setattr(st, "container", mock_container)


@pytest.fixture(autouse=True)
def mock_streamlit(monkeypatch):
    """Mock Streamlit functions for testing."""
    _mock_basic_functions(monkeypatch)
    _mock_form_functions(monkeypatch)
    _mock_layout_functions(monkeypatch)


@pytest.fixture
def mock_session_state(monkeypatch):
    """Mock Streamlit's session state for testing."""
    session_state = {}
    monkeypatch.setattr(st, "session_state", session_state)
    return session_state


@pytest.mark.asyncio
async def test_bookmark_article_success(mock_session_state):
    """Test successful article bookmarking."""
    article = {
        "title": "Test Article",
        "url": "https://example.com",
        "source": "Test Source",
        "description": "Test description",
        "published_at": "2024-03-15T12:00:00Z"
    }

    with patch(
        "src.pages.search.create_bookmark",
        new_callable=AsyncMock
    ) as mock_create:
        await bookmark_article(article)
        mock_create.assert_called_once()
        assert mock_session_state["bookmark_success"] is True


@pytest.mark.asyncio
async def test_bookmark_article_failure(mock_session_state):
    """Test failed article bookmarking."""
    article = {
        "title": "Test Article",
        "url": "https://example.com",
        "source": "Test Source"
    }

    with patch(
        "src.pages.search.create_bookmark",
        new_callable=AsyncMock
    ) as mock_create:
        mock_create.side_effect = Exception("API error")
        await bookmark_article(article)
        mock_create.assert_called_once()
        assert "bookmark_success" not in mock_session_state


@pytest.mark.asyncio
async def test_search_and_display_no_query(mock_session_state):
    """Test search with no query or category."""
    mock_session_state["search_query"] = ""
    mock_session_state["search_category"] = "all"
    await search_and_display()


@pytest.mark.asyncio
async def test_search_and_display_with_results(mock_session_state):
    """Test search with results."""
    mock_session_state["search_query"] = "test"
    mock_session_state["search_category"] = "all"

    mock_articles = [
        {
            "title": "Test Article 1",
            "url": "https://example.com/1",
            "source": "Test Source"
        },
        {
            "title": "Test Article 2",
            "url": "https://example.com/2",
            "source": "Test Source"
        }
    ]

    with patch(
        "src.pages.search.search_news",
        new_callable=AsyncMock
    ) as mock_search:
        mock_search.return_value = mock_articles
        await search_and_display()
        mock_search.assert_called_once_with(
            query="test",
            category=None,
            page_size=20
        )


@pytest.mark.asyncio
async def test_search_and_display_no_results(mock_session_state):
    """Test search with no results."""
    mock_session_state["search_query"] = "test"
    mock_session_state["search_category"] = "all"

    with patch(
        "src.pages.search.search_news",
        new_callable=AsyncMock
    ) as mock_search:
        mock_search.return_value = []
        await search_and_display()
        mock_search.assert_called_once()


@pytest.mark.asyncio
async def test_search_and_display_error(mock_session_state):
    """Test search with error."""
    mock_session_state["search_query"] = "test"
    mock_session_state["search_category"] = "all"

    with patch(
        "src.pages.search.search_news",
        new_callable=AsyncMock
    ) as mock_search:
        mock_search.side_effect = Exception("API error")
        await search_and_display()
        mock_search.assert_called_once()


def test_main_with_search_query(mock_session_state):
    """Test main function with search query."""
    mock_session_state["search_query"] = "test"
    mock_session_state["search_category"] = "all"
    mock_session_state["bookmark_success"] = True

    with patch(
        "src.pages.search.search_and_display",
        new_callable=AsyncMock
    ) as mock_search:
        main()
        mock_search.assert_called_once()
        assert "bookmark_success" not in mock_session_state


def test_main_without_search_query(mock_session_state):
    """Test main function without search query."""
    mock_session_state["search_query"] = ""
    mock_session_state["search_category"] = "all"

    with patch(
        "src.pages.search.search_and_display",
        new_callable=AsyncMock
    ) as mock_search:
        main()
        mock_search.assert_called_once()
