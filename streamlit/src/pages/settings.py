"""Settings page for user preferences."""
import streamlit as st

from utils.auth import require_auth, get_current_user

# Set page configuration
st.set_page_config(
    page_title="Settings - News Aggregator",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Require authentication
require_auth()


def main():
    """Main function for the settings page."""
    st.title("Settings")

    # Get user info
    user_info = get_current_user()

    if user_info:
        st.write("### Account Information")
        st.write(f"Email: {user_info['email']}")
        st.write(f"Name: {user_info['displayName']}")

        st.divider()

        st.write("### Preferences")
        st.info(
            "More settings and preferences will be added in future updates."
        )
    else:
        st.error("Failed to load user information.")


if __name__ == "__main__":
    main()
