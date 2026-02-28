# Home page of the dashboard

# Imports
import streamlit as st

# Custom modules
from utils import *
from styles import Styles
from components import page_title

# Set up styles
styles: Styles = Styles()
styles.set_style()
palette: dict = styles.get_style()

# Set the page title
set_page_title("Home | MAT v2.0")

# Create container for the entire home page layout
with st.container(
    key="home-container",
    horizontal_alignment="center",
    vertical_alignment="center",
):
    # Add CSS for container layout
    st.html(
        """
        <style>
            .st-key-home-container {
                min-height: calc(100vh - 15rem);
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
        </style>
    """
    )

    # Display the centered title
    page_title("Match Analysis Tool", is_home=True, palette=palette)

    # Second row: Three buttons
    button_container = st.container(
        key="nav-button-container",
        horizontal=True,
        horizontal_alignment="center",
        vertical_alignment="center",
    )

    if button_container.button(
        "Match Analysis",
        key="match_button",
    ):
        st.switch_page("pages/match.py")
    if button_container.button(
        "Team Analysis",
        key="team_button",
    ):
        st.switch_page("pages/team.py")
    if button_container.button(
        "Player Analysis",
        key="player_button",
    ):
        st.switch_page("pages/player.py")
