"""News article card component."""
import streamlit as st
from typing import Dict, Any, Callable, Optional
from datetime import datetime


def format_date(date_str: Optional[str]) -> str:
    """Format date string.

    Args:
        date_str: Date string in ISO format.

    Returns:
        str: Formatted date string.
    """
    if not date_str:
        return "Unknown date"

    try:
        date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return date.strftime("%B %d, %Y")
    except (ValueError, TypeError):
        return "Unknown date"


def article_card(
    article: Dict[str, Any],
    on_bookmark: Optional[Callable[[Dict[str, Any]], None]] = None,
    on_remove_bookmark: Optional[Callable[[int], None]] = None,
    is_bookmarked: bool = False,
    bookmark_id: Optional[int] = None
) -> None:
    """Render a news article card.

    Args:
        article: News article data.
        on_bookmark: Callback function to bookmark an article.
        on_remove_bookmark: Callback function to remove a bookmark.
        is_bookmarked: Whether the article is bookmarked.
        bookmark_id: ID of the bookmark, if bookmarked.
    """
    with st.container():
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"### [{article['title']}]({article['url']})")

            if article.get('description'):
                st.markdown(article['description'])

            meta_text = f"Source: **{article['source']}**"

            if article.get('published_at'):
                meta_text += f" | {format_date(article['published_at'])}"

            if article.get('author'):
                meta_text += f" | By {article['author']}"

            if article.get('category'):
                meta_text += f" | Category: {article['category']}"

            st.markdown(meta_text)

        with col2:
            if article.get('image_url'):
                st.image(
                    article['image_url'],
                    use_column_width=True
                )

            if on_bookmark and not is_bookmarked:
                if st.button(
                    "Bookmark",
                    key=f"bookmark_{article.get('id', hash(article['title']))}"
                ):
                    on_bookmark(article)

            if on_remove_bookmark and is_bookmarked and bookmark_id:
                if st.button(
                    "Remove Bookmark",
                    key=f"remove_bookmark_{bookmark_id}"
                ):
                    on_remove_bookmark(bookmark_id)

        st.divider()
