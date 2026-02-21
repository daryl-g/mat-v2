# Imports
import streamlit as st


# Custom navigation component
def navigation() -> None:
    """
    Custom wrapper for Streamlit's navigation element.

    Returns:
        (None): Renders the page with the navigation component.
    """
    pages: list = [
        st.Page(
            page="pages/home.py",
            title="Home",
            default=True,
        ),
        st.Page(
            page="pages/match.py",
            title="Match Analysis",
        ),
        st.Page(
            page="pages/team.py",
            title="Team Analysis",
        ),
        st.Page(
            page="pages/player.py",
            title="Player Analysis",
        ),
    ]

    pg = st.navigation(pages, position="hidden")
    pg.run()
