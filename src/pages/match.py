# Match analysis dashboard

# Imports
import streamlit as st

# Custom modules
from utils import *
from services import *
from logic import *
from vizzes import *
from styles import Styles
from components import page_title
from pages.helpers.match_helpers import (
    _stat_color,
    _render_match_header,
    _shot_summary_html,
    _PASS_CMAP_HTML,
)

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
        _render_match_header(summary_stats, "tab2", palette)

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
                        color: {_stat_color(home_val, away_val, stat_name == "Formation", palette)};
                        {'' if i == len(rows) - 1 else divider}">
                        {home_val or 0}
                    </p>
                    <p class="stats-name" style="text-align: center; margin: 0; padding: 0.3rem 0; font-weight: bold; white-space: nowrap;
                        {'' if i == len(rows) - 1 else divider}">
                        {stat_name}
                    </p>
                    <p class="away-stats" style="text-align: left; margin: 0; margin-left: 1rem; padding: 0.3rem 0;
                        color: {_stat_color(away_val, home_val, stat_name == "Formation", palette)};
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
                stats_path_xg = next(
                    (f for f in uploaded_files if f.endswith("stats.json")), ""
                )
                events_path_xg = next(
                    (f for f in uploaded_files if f.endswith("events.json")), ""
                )
                xgoal_path_xg = next(
                    (f for f in uploaded_files if f.endswith("xgoal.json")), ""
                )
                try:
                    home_kit = load_kit_colors(stats_path_xg, "home")
                    away_kit = load_kit_colors(stats_path_xg, "away")
                    configs = load_minutes(events_path_xg)
                    xg_data = load_xg_timeline(xgoal_path_xg, configs)
                    axis_configs = load_axis_configs(xg_data, configs)
                    home_shots = load_shots(xgoal_path_xg, "home")
                    away_shots = load_shots(xgoal_path_xg, "away")
                    home_name = summary_stats["matchInfo"]["homeTeam"]
                    away_name = summary_stats["matchInfo"]["awayTeam"]

                    # xG Timeline
                    xg_timeline = st.container(key="xg_timeline", border=True)
                    xg_timeline_fig = plot_xg_timeline(
                        xg_data,
                        axis_configs,
                        home_kit,
                        away_kit,
                        home_name=home_name,
                        away_name=away_name,
                    )
                    xg_timeline.pyplot(xg_timeline_fig)

                    # Shot Maps — one column per team
                    home_shots_col, away_shots_col = st.columns(
                        2, vertical_alignment="top", border=True
                    )

                    for col, name, kit, shots in [
                        (
                            home_shots_col,
                            home_name,
                            home_kit,
                            home_shots,
                        ),
                        (
                            away_shots_col,
                            away_name,
                            away_kit,
                            away_shots,
                        ),
                    ]:
                        summary = summarise_shots(shots)
                        col.html(
                            f"<p style='font-weight:bold; font-size:1.3rem; text-align:center; margin:0;'>{name}</p>"
                        )
                        col.pyplot(plot_shot_map(shots, kit))
                        col.html(_shot_summary_html(kit, summary))

                except Exception as e:
                    st.error(f"Error plotting xG & Shots: {e}")

            st.space("small")

            # Pass Networks
            with st.expander("Pass Networks", expanded=False):
                try:
                    passmap_path = next(
                        (f for f in uploaded_files if f.endswith("passmap.json")), ""
                    )
                    stats_path_pn = next(
                        (f for f in uploaded_files if f.endswith("stats.json")), ""
                    )
                    home_kit_pn = load_kit_colors(stats_path_pn, "home")
                    away_kit_pn = load_kit_colors(stats_path_pn, "away")
                    home_network = load_pass_network(passmap_path, "home")
                    away_network = load_pass_network(passmap_path, "away")
                    home_name_pn = summary_stats["matchInfo"]["homeTeam"]
                    away_name_pn = summary_stats["matchInfo"]["awayTeam"]

                    home_pass_col, away_pass_col = st.columns(
                        2, vertical_alignment="top", border=True
                    )
                    for col, name, kit, network in [
                        (home_pass_col, home_name_pn, home_kit_pn, home_network),
                        (away_pass_col, away_name_pn, away_kit_pn, away_network),
                    ]:
                        col.markdown(
                            f"<p style='font-weight:bold; font-size:1.3rem; text-align:center; margin:0;'>{name}</p>",
                            unsafe_allow_html=True,
                        )
                        col.pyplot(plot_pass_network(network, kit))
                        col.html(_PASS_CMAP_HTML)
                except Exception as e:
                    st.error(f"Error plotting Pass Networks: {e}")

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
        _render_match_header(summary_stats, "tab3", palette)

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
