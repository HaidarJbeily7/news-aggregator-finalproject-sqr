"""Search page for finding news articles."""
import streamlit as st
import asyncio
import nest_asyncio

from utils.auth import require_auth
from utils.api import search_news, create_bookmark
from components.article_card import article_card
from utils.config import NEWS_CATEGORIES

# Set page configuration
st.set_page_config(
    page_title="Search News - News Aggregator",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enable nested event loops
nest_asyncio.apply()

# Require authentication
require_auth()


async def bookmark_article(article):
    """Bookmark an article.

    Args:
        article: The article to bookmark.
    """
    try:
        bookmark_data = {
            "article_id": str(hash(article["title"])),
            "title": article["title"],
            "description": article.get("description"),
            "url": article["url"],
            "source": article["source"],
            "published_at": article.get("published_at")
        }

        await create_bookmark(bookmark_data)
        st.success("Article bookmarked successfully!")
        st.session_state["bookmark_success"] = True
    except Exception as e:
        st.error(f"Failed to bookmark article: {str(e)}")


async def search_and_display():
    """Search for news articles and display results."""
    # Get search parameters from session state
    query = st.session_state.get("search_query", "")
    category = st.session_state.get("search_category")

    if not query and category in (None, "all"):
        msg = "Enter a search query or select a category to search for news."
        st.info(msg)
        return

    with st.spinner("Searching for news..."):
        try:
            articles = await search_news(
                query=query if query else None,
                category=category if category != "all" else None,
                page_size=20
            )

            if not articles:
                st.info(
                    "No articles found. Try another search query or category."
                )
                return

            st.success(f"Found {len(articles)} articles")

            # Display articles
            for index, article in enumerate(articles):
                article_card(
                    bookmark_id=index,
                    article=article,
                    on_bookmark=lambda a=article: asyncio.run(
                        bookmark_article(a)
                    )
                )

        except Exception as e:
            st.error(f"Error searching for news: {str(e)}")


def main():
    """Main function for the search page."""
    # Display navigation
    st.title("Search News")

    # Search form
    with st.form("search_form"):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.text_input(
                "Search Query",
                key="search_query",
                placeholder="Enter keywords to search..."
            )

        with col2:
            st.selectbox(
                "Category",
                ["all"] + NEWS_CATEGORIES,
                format_func=lambda x: x.capitalize(),
                key="search_category"
            )

        submitted = st.form_submit_button("Search")

    if (submitted or st.session_state.get("search_query") or
            st.session_state.get("search_category") != "all"):
        asyncio.run(search_and_display())

    # Clear bookmark success message after displaying
    if st.session_state.get("bookmark_success"):
        del st.session_state["bookmark_success"]


if __name__ == "__main__":
    main()
