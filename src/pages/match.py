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

# Hardcoded variables
_LOWER_IS_BETTER = frozenset({"Fouls committed", "Yellow cards", "Red cards"})
data_sources = ["Opta", "StatsBomb", "SkillCorner", "Wyscout", "Blend", "Other"]
uploaded_files = st.session_state.get("uploaded_files", [])

# Auto-load from tmp folder on first run if no files are in session yet
if not uploaded_files:
    _tmp_files = load_tmp_files()
    if _tmp_files:
        st.session_state["uploaded_files"] = _tmp_files
        uploaded_files = _tmp_files

# Load all match data once; invalidate whenever uploaded_files changes
if uploaded_files and st.session_state.get("_loaded_files") != uploaded_files:
    _stats_path = next((f for f in uploaded_files if f.endswith("stats.json")), "")
    _events_path = next((f for f in uploaded_files if f.endswith("events.json")), "")
    _xgoal_path = next((f for f in uploaded_files if f.endswith("xgoal.json")), "")
    _passmap_path = next((f for f in uploaded_files if f.endswith("passmap.json")), "")
    _configs = load_minutes(_events_path)
    _xg_data = load_xg_timeline(_xgoal_path, _configs)

    st.session_state.update(
        {
            "_loaded_files": uploaded_files,
            "summary_stats": load_summary(uploaded_files),
            "stats_path": _stats_path,
            "events_path": _events_path,
            "xgoal_path": _xgoal_path,
            "passmap_path": _passmap_path,
            "home_kit": load_kit_colors(_stats_path, "home"),
            "away_kit": load_kit_colors(_stats_path, "away"),
            "home_shots": load_shots(_xgoal_path, "home"),
            "away_shots": load_shots(_xgoal_path, "away"),
            "home_network": load_pass_network(_passmap_path, "home"),
            "away_network": load_pass_network(_passmap_path, "away"),
            "configs": _configs,
            "xg_data": _xg_data,
            "axis_configs": load_axis_configs(_xg_data, _configs),
        }
    )

summary_stats = st.session_state.get("summary_stats")

# ---------------------------------------------------------------------------------------------------

# Tab container
tab1, tab2, tab3 = st.tabs(
    ["(1) Load Data", "(2) Match Summary", "(3) Detailed Analysis"],
    default="(1) Load Data",
)

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
                        color: {_stat_color(home_val, away_val, stat_name == "Formation", palette, stat_name in _LOWER_IS_BETTER)};
                        {'' if i == len(rows) - 1 else divider}">
                        {home_val or 0}
                    </p>
                    <p class="stats-name" style="text-align: center; margin: 0; padding: 0.3rem 0; font-weight: bold; white-space: nowrap;
                        {'' if i == len(rows) - 1 else divider}">
                        {stat_name}
                    </p>
                    <p class="away-stats" style="text-align: left; margin: 0; margin-left: 1rem; padding: 0.3rem 0;
                        color: {_stat_color(away_val, home_val, stat_name == "Formation", palette, stat_name in _LOWER_IS_BETTER)};
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

                stats_path = st.session_state.get("stats_path", "")
                try:
                    home_formation_fig = plot_formation(
                        stats_path=stats_path,
                        side="home",
                        vertical=True,
                    )
                    away_formation_fig = plot_formation(
                        stats_path=stats_path,
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
                        subs = load_substitutions(stats_path, side)
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
                # Layout
                home_gk_col, away_gk_col = st.columns(
                    2, vertical_alignment="top", border=True
                )
                home_players_col, away_players_col = st.columns(
                    2, vertical_alignment="top", border=True
                )
                st.write("Blah")

            st.space("small")

            # xG & Shots
            with st.expander("xG & Shots", expanded=False):
                try:
                    home_kit = st.session_state["home_kit"]
                    away_kit = st.session_state["away_kit"]
                    home_shots = st.session_state["home_shots"]
                    away_shots = st.session_state["away_shots"]
                    xg_data = st.session_state["xg_data"]
                    axis_configs = st.session_state["axis_configs"]
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
                    home_kit_pn = st.session_state["home_kit"]
                    away_kit_pn = st.session_state["away_kit"]
                    home_network = st.session_state["home_network"]
                    away_network = st.session_state["away_network"]
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

                    players_list = load_players(
                        st.session_state.get("stats_path", ""), side
                    )

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
