import pytest
from streamlit.testing.v1 import AppTest
import os


@pytest.fixture
def app():
    """Create a Streamlit app test instance."""
    # The main app file is home.py in the src directory
    script_path = os.path.join(os.path.dirname(__file__), "../src/home.py")
    assert os.path.isfile(script_path), f"File not found at {script_path}"
    return AppTest.from_file(script_path)


def test_home_page_loads(app):
    """Test that the home page loads successfully."""
    app.run()
    assert not app.exception
    # Verify that the main title is present
    assert len(app.title) > 0
    assert "News Aggregator" in app.title[0].value


def test_search_functionality(app):
    """Test the search functionality."""
    app.run()
    assert not app.exception

    # Find and interact with the search input
    search_input = app.text_input[0]
    search_input.input("technology").run()
    assert not app.exception

    # Verify that results are displayed
    assert len(app.markdown) > 0


def test_navigation_menu(app):
    """Test the navigation menu functionality."""
    app.run()
    assert not app.exception

    # Test navigation to Bookmarks
    if len(app.sidebar) > 0:
        # Click on Bookmarks in sidebar
        bookmarks_button = app.sidebar.button[0]
        bookmarks_button.click().run()
        assert not app.exception
        # Verify we're on the Bookmarks page
        assert any("Bookmarks" in markdown.value for markdown in app.markdown)


def test_article_interaction(app):
    """Test article interaction."""
    app.run()
    assert not app.exception

    # Find and click on an article
    if len(app.button) > 0:
        article_button = app.button[0]
        article_button.click().run()
        assert not app.exception
        # Verify article details are displayed
        assert len(app.markdown) > 0


def test_user_preferences(app):
    """Test user preferences and settings."""
    app.run()
    assert not app.exception

    # Test theme settings if available
    if len(app.selectbox) > 0:
        theme_selector = app.selectbox[0]
        theme_selector.select("Dark").run()
        assert not app.exception

    # Test language settings if available
    if len(app.selectbox) > 1:
        language_selector = app.selectbox[1]
        language_selector.select("English").run()
        assert not app.exception
