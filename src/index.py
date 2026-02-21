## Main entry point of the dashboard

# Imports
import streamlit as st

# Custom modules
from utils.utils import load_image
from styles import Styles

# Get colour palette
styles: Styles = Styles()
styles.set_style()

# Set default theme
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# Custom modules
from components import navigation

# Setup navigation
navigation()

st.set_page_config(
    page_icon=load_image("assets/logos/mat_logo_blue.png"),
    layout="wide",
)
