# Team analysis dashboard

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
set_page_title("Team Analysis | MAT v2.0")
