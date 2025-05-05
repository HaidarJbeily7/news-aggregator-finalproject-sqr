"""Bookmarks page for managing saved articles."""
import streamlit as st
import asyncio

from src.utils.auth import require_auth
from src.utils.api import get_bookmarks, delete_bookmark
from src.components.article_card import article_card

# Set page configuration
st.set_page_config(
    page_title="Bookmarks - News Aggregator",
    page_icon="🔖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Require authentication
require_auth()


async def remove_bookmark(bookmark_id: int) -> None:
    """Remove a bookmark.

    Args:
        bookmark_id: ID of the bookmark to remove.
    """
    try:
        await delete_bookmark(bookmark_id)
        st.success("Bookmark removed successfully!")
        st.session_state["bookmark_removed"] = True
        st.rerun()
    except Exception as e:
        st.error(f"Failed to remove bookmark: {str(e)}")


async def load_bookmarks() -> None:
    """Load and display bookmarks."""
    try:
        bookmarks = await get_bookmarks()

        if not bookmarks:
            st.info(
                "You haven't bookmarked any articles yet. "
                "Browse or search for articles to bookmark them."
            )
            return

        st.success(f"Found {len(bookmarks)} bookmarked articles")

        # Display bookmarks
        for bookmark in bookmarks:
            article = {
                "title": bookmark["title"],
                "description": bookmark.get("description"),
                "url": bookmark["url"],
                "source": bookmark["source"],
                "published_at": bookmark.get("published_at")
            }

            article_card(
                article,
                is_bookmarked=True,
                bookmark_id=bookmark["id"],
                on_remove_bookmark=lambda bid=bookmark["id"]: asyncio.run(
                    remove_bookmark(bid)
                )
            )

    except Exception as e:
        st.error(f"Error loading bookmarks: {str(e)}")


def main():
    """Main function for the bookmarks page."""
    # Display navigation
    st.title("Bookmarked Articles")

    # Load and display bookmarks
    asyncio.run(load_bookmarks())

    # Clear bookmark removal success message after displaying
    if st.session_state.get("bookmark_removed"):
        del st.session_state["bookmark_removed"]


if __name__ == "__main__":
    main()
