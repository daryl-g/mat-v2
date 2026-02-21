# Home page of the dashboard

# Imports
import streamlit as st

# Custom modules
from utils import set_page_title, load_image
from styles import Styles

# Set up styles
styles: Styles = Styles()
styles.set_style()
palette: dict = styles.get_style()

# Set the page title
set_page_title("Home | MAT v2.0")

image_path = "assets/logos/mat_logo_black.png"
image_width = 5.5
image_height = 5.5
text_1 = "Match Analysis Tool"

# Load the image as base64
try:
    image_path_b64 = load_image(image_path)
except Exception as e:
    st.error(f"Error loading image: {e}")
    image_path_b64 = None

# Create container for the entire home page layout
with st.container(
    key="home-container",
    horizontal_alignment="center",
    vertical_alignment="center",
):
    # Add CSS for centering and layout
    st.html(
        f"""
        <style>
            .st-key-home-container {{
                min-height: calc(100vh - 15rem);
                display: flex;
                flex-direction: column;
                justify-content: center;
            }}
            .centered-title {{
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 2rem 0;
            }}
            .title-content {{
                display: flex;
                align-items: center;
            }}
        </style>
    """
    )

    # First row: Title (single column)
    st.html(
        f"""
        <div class="centered-title">
            <div class="title-content">
                {f"<img src='{image_path_b64}' style='width: {image_width}rem; height: {image_height}rem;' />" if image_path_b64 is not None else ""}
                <h1 style='font-size:3.5em; color: {palette['title-color']}; font-weight: bold; margin: 0; margin-left: 1.5rem;'>
                {text_1}
                </h1>
            </div>
        </div>
    """
    )

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
