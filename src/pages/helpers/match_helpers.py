# Helper functions and constants for the Match Analysis page

# Imports
from datetime import datetime

import streamlit as st


# ---------------------------------------------------------------------------------------------------
# Stat colour


def _stat_color(
    val: str,
    other_val: str,
    is_formation: bool,
    palette: dict,
    lower_is_better: bool = False,
) -> str:
    """
    Return a highlight color based on comparison between two stat values.

    Args:
        val (str): The stat value for the team in question.
        other_val (str): The stat value for the opposing team.
        is_formation (bool): Whether the stat being compared is formation (which should not be compared numerically).
        palette (dict): The active colour palette.
        lower_is_better (bool): When True, a lower value is coloured green and a
            higher value red (e.g. fouls committed, cards). Default is False.

    Returns:
        str: A hex color code for the stat text.
    """
    if is_formation:
        return palette["alt-text-color"]
    a, b = float(val or 0), float(other_val or 0)
    if lower_is_better:
        a, b = b, a
    if a > b:
        return "#23a118"
    if a < b:
        return "#850b07"
    return "#a3a303"


# ---------------------------------------------------------------------------------------------------
# Match header renderer


def _render_match_header(summary_stats: dict, key_prefix: str, palette: dict) -> None:
    """
    Render the box score and match info header into a centered container.

    Args:
        summary_stats (dict): The match summary data.
        key_prefix (str): Unique prefix for Streamlit container keys.
        palette (dict): The active colour palette.
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
