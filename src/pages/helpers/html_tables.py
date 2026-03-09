# HTML table helpers for the Match Analysis page

# ─── Shot summary table ──────────────────────────────────────────────────────

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


# ─── Pass network colourmap legend — mirrors _PASS_CMAP stops in mpl.py ─────

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


# ─── Player stats table ───────────────────────────────────────────────────────

# Columns that should be left-aligned (everything else is right-aligned)
_LEFT_ALIGN_COLS = {"Name", "Position"}

# Width reserved for the sticky shirt-number column
_SHIRT_W = "3rem"

_PST_CSS = f"""
<style>
  .pst {{ border-collapse: collapse; font-size: 0.8rem; width: max-content; }}
  .pst th, .pst td {{
    padding: 0.2rem 0.5rem;
    white-space: nowrap;
  }}
  .pst thead tr {{ border-bottom: 1px solid rgba(128,128,128,0.3); }}
  .pst tbody tr:nth-child(even) {{ background: rgba(128,128,128,0.05); }}
  .pst .col-left  {{ text-align: left; }}
  .pst .col-right {{ text-align: right; }}
  .pst .sticky-0 {{
    position: sticky;
    left: 0;
    z-index: 2;
    background: var(--background-color, #d1e5f4);
  }}
  .pst .sticky-1 {{
    position: sticky;
    left: {_SHIRT_W};
    z-index: 2;
    background: var(--background-color, #d1e5f4);
  }}
  .pst .shirt-col {{
    text-align: center;
    min-width: {_SHIRT_W};
    width: {_SHIRT_W};
  }}
</style>
"""


def _th_align(col: str) -> str:
    return "left" if col in _LEFT_ALIGN_COLS else "right"


def _display_cell(col: str, val) -> str:
    """Suppress zero numeric values in right-aligned columns; leave strings untouched."""
    if col not in _LEFT_ALIGN_COLS:
        try:
            if float(val) == 0:
                return ""
        except (TypeError, ValueError):
            pass
    return str(val) if val is not None else ""


def _player_stats_html(kit: dict, df) -> str:
    """
    Render a player stats DataFrame as a styled HTML table.

    The first two columns (shirt number + Name) are sticky so they remain
    visible while the user scrolls horizontally.  Zero values are suppressed
    (displayed as an empty cell).  The table is wrapped in an overflow-x:auto
    container to prevent it from overflowing the parent widget.

    Args:
        kit (dict): Kit colours dict, must contain ``"colour1"``.
        df: pandas DataFrame with ``#`` as index.

    Returns:
        str: An HTML string suitable for ``st.html()``.
    """
    if df is None or len(df) == 0:
        return (
            "<p style='color:grey; font-size:0.85rem; margin:0;'>No data available.</p>"
        )

    color = kit["colour1"]
    columns = list(df.columns)

    th_cells = "<th class='sticky-0 shirt-col'>#</th>" + "".join(
        f"<th class='col-{_th_align(col)}{' sticky-1' if col == 'Name' else ''}'>{col}</th>"
        for col in columns
    )

    rows_html = "".join(
        "<tr>"
        f"<td class='sticky-0 shirt-col' style='color:{color}; font-weight:bold;'>{idx}</td>"
        + "".join(
            f"<td class='col-{_th_align(col)}{' sticky-1' if col == 'Name' else ''}'>{_display_cell(col, val)}</td>"
            for col, val in row.items()
        )
        + "</tr>"
        for idx, row in df.iterrows()
    )

    return f"""
    {_PST_CSS}
    <div style="width:100%; overflow-x:auto;">
      <table class="pst">
        <thead><tr>{th_cells}</tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    """
