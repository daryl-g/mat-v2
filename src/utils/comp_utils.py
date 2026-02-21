# Utility functions for component rendering and styling

# Imports
import streamlit as st


def set_page_title(title: str) -> None:
    """
    Set the page title for the Streamlit app.

    Args:
        title (str): The title to set for the page.
    """
    st.set_page_config(page_title=title)
