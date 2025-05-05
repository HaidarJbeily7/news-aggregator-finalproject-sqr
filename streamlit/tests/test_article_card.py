import pytest
import streamlit as st
from src.components.article_card import format_date, article_card


class MockContainer:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture(autouse=True)
def mock_streamlit(monkeypatch):
    """Mock Streamlit functions for testing."""
    def mock_markdown(text):
        return text

    def mock_container():
        return MockContainer()

    def mock_columns(ratio):
        return [MockContainer(), MockContainer()]

    def mock_image(url, use_column_width):
        return url

    def mock_button(text, key):
        return False

    def mock_divider():
        return None

    monkeypatch.setattr(st, "markdown", mock_markdown)
    monkeypatch.setattr(st, "container", mock_container)
    monkeypatch.setattr(st, "columns", mock_columns)
    monkeypatch.setattr(st, "image", mock_image)
    monkeypatch.setattr(st, "button", mock_button)
    monkeypatch.setattr(st, "divider", mock_divider)


def test_format_date_valid():
    """Test formatting a valid date string."""
    date_str = "2024-03-15T12:00:00Z"
    formatted = format_date(date_str)
    assert formatted == "March 15, 2024"


def test_format_date_invalid():
    """Test formatting an invalid date string."""
    date_str = "invalid-date"
    formatted = format_date(date_str)
    assert formatted == "Unknown date"


def test_format_date_none():
    """Test formatting a None date."""
    formatted = format_date(None)
    assert formatted == "Unknown date"


def test_article_card_basic():
    """Test rendering a basic article card."""
    article = {
        "title": "Test Article",
        "url": "https://example.com",
        "source": "Test Source",
        "description": "Test description",
        "published_at": "2024-03-15T12:00:00Z",
        "author": "Test Author",
        "category": "Test Category",
        "image_url": "https://example.com/image.jpg"
    }

    # Test without bookmark callbacks
    article_card(article)


def test_article_card_with_bookmark():
    """Test article card with bookmark functionality."""
    article = {
        "title": "Test Article",
        "url": "https://example.com",
        "source": "Test Source"
    }

    bookmark_called = False
    remove_bookmark_called = False

    def on_bookmark(article_data):
        nonlocal bookmark_called
        bookmark_called = True
        assert article_data == article

    def on_remove_bookmark(bookmark_id):
        nonlocal remove_bookmark_called
        remove_bookmark_called = True
        assert bookmark_id == 123

    # Test bookmark button
    article_card(article, on_bookmark=on_bookmark)
    assert not bookmark_called  # Button wasn't clicked

    # Test remove bookmark button
    article_card(
        article,
        on_remove_bookmark=on_remove_bookmark,
        is_bookmarked=True,
        bookmark_id=123
    )
    assert not remove_bookmark_called  # Button wasn't clicked


def test_article_card_minimal():
    """Test rendering an article card with minimal data."""
    article = {
        "title": "Test Article",
        "url": "https://example.com",
        "source": "Test Source"
    }

    article_card(article)
