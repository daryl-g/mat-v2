# Match analysis dashboard

# Imports
import streamlit as st

# Custom modules
from utils import set_page_title
from services.data_loaders import (
    render_opta_wyscout_inputs,
    render_statsbomb_skillcorner_inputs,
    render_blend_inputs,
    render_other_inputs,
)
from styles import Styles
from components import page_title

# Set up styles
styles: Styles = Styles()
styles.set_style()
palette: dict = styles.get_style()

# Set the page title
set_page_title("Match Analysis | MAT v2.0")

# Display title
page_title("Match Analysis Tool", is_home=False, palette=palette)

# ---------------------------------------------------------------------------------------------------

# Tab container
tab1, tab2 = st.tabs(
    ["(1) Load Data", "(2) Explore & Analyse"],
    default="(1) Load Data",
)

# Hardcoded variables
data_sources = ["Opta", "StatsBomb", "SkillCorner", "Wyscout", "Blend", "Other"]

with tab1:
    st.html("""<p style="font-weight: bold; font-size: 2rem;">Choose data source</p>""")

    # Data source selection
    data_source = st.selectbox(
        "Select data source:",
        options=data_sources,
        index=0,
    )

    # Render appropriate inputs based on selected data source
    if data_source in ["Opta", "Wyscout"]:
        uploaded_files = render_opta_wyscout_inputs()
    elif data_source in ["StatsBomb", "SkillCorner"]:
        source_type = render_statsbomb_skillcorner_inputs(data_source)
    elif data_source == "Blend":
        selected_sources = render_blend_inputs(data_sources)
    elif data_source == "Other":
        other_source = render_other_inputs()
