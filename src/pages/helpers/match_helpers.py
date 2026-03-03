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


# ---------------------------------------------------------------------------------------------------
# Shot summary table


_OUTCOME_ROWS = [
    ("&#9679;", "Goal", "goals"),
    ("&#9650;", "On target", "saved"),
    ("&#9632;", "Hit post", "post"),
    ("&#9670;", "Blocked", "blocked"),
    ("&#10005;", "Off target", "off_target"),
]


def _shot_summary_html(kit: dict, summary: dict) -> str:
    color = kit["colour1"]
    rows_html = "".join(
        f"""
        <tr>
            <td style="text-align:center; padding:0.2rem 0.5rem; color:{color}; font-size:1rem;">{sym}</td>
            <td style="padding:0.2rem 0.5rem;">{label}</td>
            <td style="text-align:right; padding:0.2rem 0.5rem;">{summary[key]['count']}</td>
            <td style="text-align:right; padding:0.2rem 0.5rem;">{summary[key]['xg']:.2f}</td>
        </tr>
        """
        for sym, label, key in _OUTCOME_ROWS
    )
    # Addendum rows for penalties and own goals (only rendered when count > 0)
    addendum_rows = ""
    if summary["penalties"]["count"] > 0:
        pen_xg = summary["penalties"]["xg"]
        if summary["penalties"]["scored"] > 0:
            n = summary["penalties"]["scored"]
            addendum_rows += f"""
        <tr style="color:rgba(128,128,128,0.8); font-style:italic; font-size:0.8rem;">
            <td style="text-align:center; padding:0.1rem 0.5rem; color:{color}; font-size:1rem;">&#9679;</td>
            <td style="padding:0.1rem 0.5rem;">+ {n} {'penalty' if n == 1 else 'penalties'} scored</td>
            <td style="text-align:right; padding:0.1rem 0.5rem;">{n}</td>
            <td style="text-align:right; padding:0.1rem 0.5rem;">+{pen_xg * n / summary['penalties']['count']:.2f}</td>
        </tr>
        """
        if summary["penalties"]["missed"] > 0:
            n = summary["penalties"]["missed"]
            addendum_rows += f"""
        <tr style="color:rgba(128,128,128,0.8); font-style:italic; font-size:0.8rem;">
            <td style="text-align:center; padding:0.1rem 0.5rem; color:{color}; font-size:1rem;">&#10005;</td>
            <td style="padding:0.1rem 0.5rem;">+ {n} {'penalty' if n == 1 else 'penalties'} missed</td>
            <td style="text-align:right; padding:0.1rem 0.5rem;">{n}</td>
            <td style="text-align:right; padding:0.1rem 0.5rem;">+{pen_xg * n / summary['penalties']['count']:.2f}</td>
        </tr>
        """
    if summary["own_goals"]["count"] > 0:
        n = summary["own_goals"]["count"]
        addendum_rows += f"""
        <tr style="color:rgba(128,128,128,0.8); font-style:italic; font-size:0.8rem;">
            <td style="text-align:center; padding:0.1rem 0.5rem; color:{color};">&#9679;</td>
            <td style="padding:0.1rem 0.5rem;">+ {n} own {'goal' if n == 1 else 'goals'}</td>
            <td style="text-align:right; padding:0.1rem 0.5rem;">{n}</td>
            <td style="text-align:right; padding:0.1rem 0.5rem;">&#8212;</td>
        </tr>
        """
    return f"""
    <table style="width:100%; border-collapse:collapse; font-size:0.85rem;">
        <thead>
            <tr style="border-bottom:1px solid rgba(128,128,128,0.3);">
                <th style="padding:0.2rem 0.5rem;"></th>
                <th style="text-align:left; padding:0.2rem 0.5rem;">Outcome</th>
                <th style="text-align:right; padding:0.2rem 0.5rem;">Shots</th>
                <th style="text-align:right; padding:0.2rem 0.5rem;">npxG</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
            <tr style="border-top:1px solid rgba(128,128,128,0.3); font-weight:bold;">
                <td></td>
                <td style="padding:0.2rem 0.5rem;">Total</td>
                <td style="text-align:right; padding:0.2rem 0.5rem;">{summary['total']['count']}</td>
                <td style="text-align:right; padding:0.2rem 0.5rem;">{summary['total']['xg']:.2f}</td>
            </tr>
            {addendum_rows}
        </tbody>
    </table>
    <p style="text-align:center; font-size:0.7rem; color:grey; margin-top:0.3rem;">Marker size correlates to xG value</p>
    """


# ---------------------------------------------------------------------------------------------------
# Pass network colourmap legend — mirrors _PASS_CMAP stops in mpl.py

_PASS_CMAP_HTML = """
<div style="padding:0.4rem 0.5rem 0.2rem;">
    <p style="text-align:center; font-size:0.7rem; color:grey; margin:0 0 0.4rem;">
        Node size correlates to player's accurate passes
    </p>
    <div style="
        height: 10px;
        border-radius: 4px;
        background: linear-gradient(to right, #a5b4fc, #6366f1, #4c1d95);
        margin-bottom: 0.25rem;
    "></div>
    <div style="display:flex; justify-content:space-between; font-size:0.7rem; color:grey;">
        <span>Fewer combinations</span>
        <span>More combinations</span>
    </div>
</div>
"""
