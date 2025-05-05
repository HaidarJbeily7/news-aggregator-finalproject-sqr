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
        _render_article_content(article)
        _handle_bookmark_actions(
            article,
            on_bookmark,
            on_remove_bookmark,
            is_bookmarked,
            bookmark_id
        )
        st.divider()


def _render_article_content(article: Dict[str, Any]) -> None:
    """Render the article content.

    Args:
        article: News article data.
    """
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"### [{article['title']}]({article['url']})")

        if article.get('description'):
            st.markdown(article['description'])

        meta_text = _build_meta_text(article)
        st.markdown(meta_text)

    with col2:
        if article.get('image_url'):
            st.image(
                article['image_url'],
                use_column_width=True
            )


def _build_meta_text(article: Dict[str, Any]) -> str:
    """Build the meta text for the article.

    Args:
        article: News article data.

    Returns:
        str: Formatted meta text.
    """
    meta_text = f"Source: **{article['source']}**"

    if article.get('published_at'):
        meta_text += f" | {format_date(article['published_at'])}"

    if article.get('author'):
        meta_text += f" | By {article['author']}"

    if article.get('category'):
        meta_text += f" | Category: {article['category']}"

    return meta_text


def _handle_bookmark_actions(
    article: Dict[str, Any],
    on_bookmark: Optional[Callable[[Dict[str, Any]], None]],
    on_remove_bookmark: Optional[Callable[[int], None]],
    is_bookmarked: bool,
    bookmark_id: Optional[int]
) -> None:
    """Handle bookmark and remove bookmark actions.

    Args:
        article: News article data.
        on_bookmark: Callback function to bookmark an article.
        on_remove_bookmark: Callback function to remove a bookmark.
        is_bookmarked: Whether the article is bookmarked.
        bookmark_id: ID of the bookmark, if bookmarked.
    """
    col1, col2 = st.columns([3, 1])

    with col2:
        if on_bookmark and not is_bookmarked and st.button(
            "Bookmark",
            key=f"bookmark_{hash(article['title'])}"
        ):
            on_bookmark(article)

        if (
            on_remove_bookmark
            and is_bookmarked
            and bookmark_id
            and st.button(
                "Remove Bookmark",
                key=f"remove_bookmark_{bookmark_id}",
            )
        ):
            on_remove_bookmark(bookmark_id)
