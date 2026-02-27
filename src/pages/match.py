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


def _stat_color(val: str, other_val: str, is_formation: bool) -> str:
    """
    Return a highlight color based on comparison between two stat values.

    Args:
        val (str): The stat value for the team in question.
        other_val (str): The stat value for the opposing team.
        is_formation (bool): Whether the stat being compared is formation (which should not be compared numerically).

    Returns:
        str: A hex color code for the stat text.
    """
    if is_formation:
        return palette["alt-text-color"]
    a, b = float(val or 0), float(other_val or 0)
    if a > b:
        return "#2d7a4f"
    if a < b:
        return "#c20d00"
    return "#a3a303"


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
        summary_container = st.container(
            key="summary_stats", horizontal_alignment="center", gap=None
        )
        vizzes_container = st.container(
            key="vizzes", horizontal_alignment="center", gap=None
        )

        # Load summary stats
        summary_stats = load_summary(uploaded_files)

        # Layout for summary container
        with summary_container:

            box_score = st.container(key="box_score", gap=None)
            match_info = st.container(key="match_info", gap=None)

            # Text elements
            box_score.html(
                f"""
                <div class="box-score" style="display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 1rem;">
                    <p style="font-weight: bold; font-size: 1.2rem; text-align: right; margin-bottom: 0.4rem;">{summary_stats['matchInfo']['homeTeam']}</p>
                    <p style="width: 4rem; font-weight: bold; font-size: 1.7rem; text-align: center; margin-bottom: 0.4rem; margin-left: 0.5rem; margin-right: 0.5rem;">{summary_stats['matchInfo']['scores']["ft"]["home"]} - {summary_stats['matchInfo']['scores']["ft"]["away"]}</p>
                    <p style="font-weight: bold; font-size: 1.2rem; text-align: left; margin-bottom: 0.4rem;">{summary_stats['matchInfo']['awayTeam']}</p>
                </div>
                """
            )
            # Competition and date
            match_info.html(
                f"""
                <div class="comp-and-date" style="display: flex; flex-direction: column; align-items: center; gap: 0rem;">
                    <p style="font-size: 1rem; font-weight: light; text-align: center; color: {palette['text-color']}; margin-bottom: 0.4rem;">{summary_stats['matchInfo']['competition']}</p>
                    <p style="font-size: 0.9rem; font-weight: light; text-align: center; color: {palette['text-color']};">{summary_stats['matchInfo']['date']}</p>
                </div>
                """
            )

        # Layout for vizzes container
        with vizzes_container:
            match_stats = summary_stats["matchStats"]

            # Summary stats
            with st.expander("Match Summary", expanded=True):
                home_vals = list(match_stats["home"].values())
                stat_names = list(match_stats["home"].keys())
                away_vals = list(match_stats["away"].values())

                rows = list(zip(home_vals, stat_names, away_vals))
                divider = "border-bottom: 1px solid rgba(128,128,128,0.2);"

                cells_html = "".join(
                    f"""
                    <p style="text-align: right; margin: 0; margin-right: 1rem; padding: 0.3rem 0;
                        color: {_stat_color(home_val, away_val, stat_name == "Formation")};
                        {'' if i == len(rows) - 1 else divider}">
                        {home_val or 0}
                    </p>
                    <p style="text-align: center; margin: 0; padding: 0.3rem 0; font-weight: bold; white-space: nowrap;
                        {'' if i == len(rows) - 1 else divider}">
                        {stat_name}
                    </p>
                    <p style="text-align: left; margin: 0; margin-left: 1rem; padding: 0.3rem 0;
                        color: {_stat_color(away_val, home_val, stat_name == "Formation")};
                        {'' if i == len(rows) - 1 else divider}">
                        {away_val or 0}
                    </p>
                    """
                    for i, (home_val, stat_name, away_val) in enumerate(rows)
                )
                st.html(
                    f"""
                    <div style="display: grid; grid-template-columns: 1fr auto 1fr; align-items: center;
                        column-gap: 0.5rem; width: 100%; max-width: 600px; margin: 0 auto;">
                        {cells_html}
                    </div>
                    """
                )


with tab3:
    # Check if any files have been uploaded
    if len(uploaded_files) == 0:
        st.error(
            "No data files found. Please go back to the 'Load Data' tab and upload your files."
        )
    else:
        # Layout setup
        viz_col, control_panel = st.columns([65, 35], vertical_alignment="top")
