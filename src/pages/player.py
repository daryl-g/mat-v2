# Player data dashboard

# Imports
import streamlit as st

# Custom modules
from utils import set_page_title
from styles import Styles
from components import page_title

# Set up styles
styles: Styles = Styles()
styles.set_style()
palette: dict = styles.get_style()

# Set the page title
set_page_title("Player Analysis | MAT v2.0")

# Display title
page_title("Match Analysis Tool", is_home=False, palette=palette)
