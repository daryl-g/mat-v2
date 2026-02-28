# Match analysis dashboard

# Imports
from datetime import datetime

import streamlit as st

# Custom modules
from utils import set_page_title
from services import (
    render_opta_wyscout_inputs,
    render_statsbomb_skillcorner_inputs,
    render_blend_inputs,
    render_other_inputs,
)
from logic import load_summary, load_formation, load_substitutions, load_players
from vizzes import plot_formation
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
# Helper functions


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
        return "#23a118"
    if a < b:
        return "#850b07"
    return "#a3a303"


def _render_match_header(summary_stats: dict, key_prefix: str) -> None:
    """
    Render the box score and match info header into a centered container.

    Args:
        summary_stats (dict): The match summary data.
        key_prefix (str): Unique prefix for Streamlit container keys.
    """
    with st.container(
        key=f"{key_prefix}_summary", horizontal_alignment="center", gap=None
    ):
        box_score = st.container(key=f"{key_prefix}_box_score", gap=None)
        match_info_container = st.container(key=f"{key_prefix}_match_info", gap=None)

        box_score.html(
            f"""
            <div class="box-score" style="display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 1rem;">
                <p style="font-weight: bold; font-size: 1.2rem; text-align: right; margin-bottom: 0.4rem;">{summary_stats['matchInfo']['homeTeam']}</p>
                <p style="width: 4rem; font-weight: bold; font-size: 1.7rem; text-align: center; margin-bottom: 0.4rem; margin-left: 0.5rem; margin-right: 0.5rem;">{summary_stats['matchInfo']['scores']["ft"]["home"]} - {summary_stats['matchInfo']['scores']["ft"]["away"]}</p>
                <p style="font-weight: bold; font-size: 1.2rem; text-align: left; margin-bottom: 0.4rem;">{summary_stats['matchInfo']['awayTeam']}</p>
            </div>
            """
        )
        info = summary_stats["matchInfo"]
        competition_parts = [
            info["competition"],
            info["tournamentCalendar"],
            info["stage"],
        ]
        competition_line = " · ".join(p for p in competition_parts if p)
        formatted_date = (
            datetime.strptime(info["date"], "%Y-%m-%d").strftime("%B %d, %Y")
            if info["date"]
            else ""
        )

        match_info_container.html(
            f"""
            <div class="comp-and-date" style="display: flex; flex-direction: column; align-items: center; gap: 0rem;">
                <p style="font-size: 1rem; font-weight: light; text-align: center; color: {palette['alt-text-color']}; margin-bottom: 0.4rem;">{competition_line}</p>
                <p style="font-size: 0.9rem; font-weight: light; text-align: center; color: {palette['alt-text-color']};">{formatted_date}</p>
            </div>
            """
        )


# ---------------------------------------------------------------------------------------------------

# Tab container
tab1, tab2, tab3 = st.tabs(
    ["(1) Load Data", "(2) Match Summary", "(3) Detailed Analysis"],
    default="(1) Load Data",
)

# Hardcoded variables
data_sources = ["Opta", "StatsBomb", "SkillCorner", "Wyscout", "Blend", "Other"]
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

# Load summary stats once, shared across tabs
summary_stats = load_summary(uploaded_files) if uploaded_files else None

with tab2:
    # Check if any files have been uploaded
    if len(uploaded_files) == 0:
        st.error(
            "No data files found. Please go back to the 'Load Data' tab and upload your files."
        )
    else:
        # Match header
        _render_match_header(summary_stats, "tab2")

        # Visualisations
        vizzes_container = st.container(
            key="vizzes", horizontal_alignment="center", gap=None
        )

        # Layout for vizzes container
        with vizzes_container:
            match_stats = summary_stats["matchStats"]

            # Match Summary
            with st.expander("Match Summary", expanded=True):
                home_vals = list(match_stats["home"].values())
                stat_names = list(match_stats["home"].keys())
                away_vals = list(match_stats["away"].values())

                rows = [
                    (h, s, a)
                    for h, s, a in zip(home_vals, stat_names, away_vals)
                    if s != "Formation"
                ]
                divider = "border-bottom: 1px solid rgba(128,128,128,0.2);"

                cells_html = "".join(
                    f"""
                    <p class="home-stats" style="text-align: right; margin: 0; margin-right: 1rem; padding: 0.3rem 0;
                        color: {_stat_color(home_val, away_val, stat_name == "Formation")};
                        {'' if i == len(rows) - 1 else divider}">
                        {home_val or 0}
                    </p>
                    <p class="stats-name" style="text-align: center; margin: 0; padding: 0.3rem 0; font-weight: bold; white-space: nowrap;
                        {'' if i == len(rows) - 1 else divider}">
                        {stat_name}
                    </p>
                    <p class="away-stats" style="text-align: left; margin: 0; margin-left: 1rem; padding: 0.3rem 0;
                        color: {_stat_color(away_val, home_val, stat_name == "Formation")};
                        {'' if i == len(rows) - 1 else divider}">
                        {away_val or 0}
                    </p>
                    """
                    for i, (home_val, stat_name, away_val) in enumerate(rows)
                )
                st.html(
                    f"""
                    <div class="summary-stats-cols" style="display: grid; grid-template-columns: 1fr auto 1fr; align-items: center;
                        column-gap: 0.5rem; width: 100%; max-width: 600px; margin: 0 auto;">
                        {cells_html}
                    </div>
                    """
                )

            st.space("small")

            # Lineups
            with st.expander("Lineups", expanded=False):
                home_formation_col, away_formation_col = st.columns(
                    2, vertical_alignment="top", border=True
                )

                home_formation = match_stats["home"].get("Formation", "")
                away_formation = match_stats["away"].get("Formation", "")

                home_formation_col.html(
                    f"""
                    <div class="home-formation" style="display: flex; flex-direction: row; align-items: baseline; column-gap: 0.5rem;">
                        <p style="font-weight: bold; font-size: 1.2rem; margin: 0;">{summary_stats['matchInfo']['homeTeam']}</p>
                        <p style="font-size: 1.2rem; color: {palette['alt-text-color']}; margin: 0;">({home_formation})</p>
                    </div>
                    """
                )
                away_formation_col.html(
                    f"""
                    <div class="away-formation" style="display: flex; flex-direction: row; align-items: baseline; column-gap: 0.5rem;">
                        <p style="font-weight: bold; font-size: 1.2rem; margin: 0;">{summary_stats['matchInfo']['awayTeam']}</p>
                        <p style="font-size: 1.2rem; color: {palette['alt-text-color']}; margin: 0;">({away_formation})</p>
                    </div>
                    """
                )

                stats_file_path = next(
                    (f for f in uploaded_files if f.endswith("stats.json")), ""
                )
                try:
                    home_formation_fig = plot_formation(
                        stats_path=stats_file_path,
                        side="home",
                        vertical=True,
                    )
                    away_formation_fig = plot_formation(
                        stats_path=stats_file_path,
                        side="away",
                        vertical=True,
                    )
                    home_formation_col.pyplot(home_formation_fig)
                    away_formation_col.pyplot(away_formation_fig)

                    # Substitutions
                    for col, side in [
                        (home_formation_col, "home"),
                        (away_formation_col, "away"),
                    ]:
                        subs = load_substitutions(stats_file_path, side)
                        if subs:
                            rows_html = "".join(
                                f"""
                                <div style="display: contents;">
                                    <div style="margin-bottom: 0.4rem;">
                                        <p style="margin: 0; font-size: 1rem; color: #23a118;">▲ {on}</p>
                                        <p style="margin: 0; font-size: 1rem; color: #850b07;">▼ {off}</p>
                                    </div>
                                    <p style="margin: 0 0 0.4rem 0; font-size: 1rem; color: {palette['alt-text-color']}; white-space: nowrap;">{t}</p>
                                </div>
                                """
                                for off, on, t in subs
                            )
                            col.html(
                                f"""
                                <p style="margin: 0; font-size: 1rem; font-weight: bold; color: {palette['title-color']};">Substitutions</p>
                                <div style="display: grid; grid-template-columns: 1fr auto; column-gap: 0.75rem; padding: 0.4rem 0; align-items: start;">
                                    {rows_html}
                                </div>
                                """
                            )

                except Exception as e:
                    st.error(f"Error plotting formations: {e}")

            st.space("small")

            # Player Stats
            with st.expander("Player Stats", expanded=False):
                home_players_col, away_players_col = st.columns(
                    2, vertical_alignment="top", border=True
                )
                st.write("Blah")

            st.space("small")

            # xG & Shots
            with st.expander("xG & Shots", expanded=False):
                xg_timeline = st.container(key="xg_timeline", border=True)
                shots_map = st.container(key="shots_map")
                home_shots_col, away_shots_col = shots_map.columns(
                    2, vertical_alignment="top", border=True
                )
                st.write("Blah")

            st.space("small")

            # Pass Networks
            with st.expander("Pass Networks", expanded=False):
                home_pass_col, away_pass_col = st.columns(
                    2, vertical_alignment="top", border=True
                )
                st.write("Blah")

            st.space("small")

            # Possession
            with st.expander("Possession", expanded=False):
                st.write("Blah")


with tab3:
    # Check if any files have been uploaded
    if len(uploaded_files) == 0:
        st.error(
            "No data files found. Please go back to the 'Load Data' tab and upload your files."
        )
    else:
        # Match header
        _render_match_header(summary_stats, "tab3")

        detailed_mode = st.container(
            key="detailed_mode",
            horizontal=True,
            horizontal_alignment="center",
            gap=None,
        )
        # Mode selection — persist active mode in session state so reruns don't reset it
        if detailed_mode.button("Team-level", key="team_detailed", type="secondary"):
            st.session_state["detailed_active_mode"] = "team"
        detailed_mode.space("small")
        if detailed_mode.button(
            "Player-level", key="player_detailed", type="secondary"
        ):
            st.session_state["detailed_active_mode"] = "player"

        active_mode = st.session_state.get("detailed_active_mode")

        if active_mode in ("team", "player"):
            # Layout setup
            control_panel, viz_col = st.columns([35, 65], vertical_alignment="center")

            with control_panel:
                # Main selection widgets
                team_selection = [
                    summary_stats["matchInfo"]["homeTeam"],
                    summary_stats["matchInfo"]["awayTeam"],
                ]
                detailed_team_selected = st.selectbox(
                    "Select team:",
                    options=team_selection,
                    key="detailed_team_selected",
                )
                if active_mode == "player":
                    side = (
                        "home"
                        if detailed_team_selected
                        == summary_stats["matchInfo"]["homeTeam"]
                        else "away"
                    )

                    stats_file = next(
                        (f for f in uploaded_files if f.endswith("stats.json")), ""
                    )
                    players_list = load_players(stats_file, side)

                    # Prefix with shirt number if available
                    players_list = [
                        f"#{shirt} - {name}" if shirt else name
                        for shirt, name in players_list.values()
                    ]

                    detailed_player_selected = st.selectbox(
                        "Select player:",
                        options=players_list,
                        key="detailed_player_selected",
                    )
