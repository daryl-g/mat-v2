# Match analysis dashboard

# Imports
import streamlit as st

# Custom modules
from utils import set_page_title
from services import (
    render_opta_wyscout_inputs,
    render_statsbomb_skillcorner_inputs,
    render_blend_inputs,
    render_other_inputs,
    load_summary,
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
tab1, tab2, tab3 = st.tabs(
    ["(1) Load Data", "(2) Match Summary", "(3) Detailed Analysis"],
    default="(1) Load Data",
)

# Hardcoded variables
data_sources = ["Opta", "StatsBomb", "SkillCorner", "Wyscout", "Blend", "Other"]
vizzes_options = ["xG Timeline", "Pass Network", "Shot Map"]
uploaded_files = []

with tab1:
    st.html("""<p style="font-weight: bold; font-size: 2rem;">Choose data source</p>""")

    # Data source selection
    data_source = st.selectbox(
        "Select data source:",
        options=data_sources,
        key="data_source",
        index=0,
    )

    # Render appropriate inputs based on selected data source
    if data_source in ["Opta", "Wyscout"]:
        uploaded_files = render_opta_wyscout_inputs(data_source)
    elif data_source in ["StatsBomb", "SkillCorner"]:
        source_type = render_statsbomb_skillcorner_inputs(data_source)
    elif data_source == "Blend":
        selected_sources = render_blend_inputs(data_sources)
    elif data_source == "Other":
        other_source = render_other_inputs()

with tab2:
    # Check if any files have been uploaded
    if len(uploaded_files) == 0:
        st.error(
            "No data files found. Please go back to the 'Load Data' tab and upload your files."
        )
    else:
        # Layout setup
        left_col, mid_col, right_col = st.columns(
            [29, 42, 29], vertical_alignment="top"
        )

        # Left col: Top: Vertical home pass network, Bottom: Home player stats
        # Mid col: Top: Match summary stats, Bottom: xG timeline + home & away shot maps
        # Right col: Top: Vertical away pass network, Bottom: Away player stats

        # Load and display match summary
        with mid_col:
            st.html(
                """<p style="font-weight: bold; font-size: 2rem;">Match Summary</p>"""
            )
            summary_dict = load_summary(uploaded_files)
            st.json(summary_dict)

with tab3:
    # Check if any files have been uploaded
    if len(uploaded_files) == 0:
        st.error(
            "No data files found. Please go back to the 'Load Data' tab and upload your files."
        )
    else:
        # Layout setup
        viz_col, control_panel = st.columns([65, 35], vertical_alignment="top")
