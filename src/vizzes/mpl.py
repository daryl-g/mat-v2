# Static vizzes using matplotlib and mplsoccer

# Imports
import copy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Custom modules
from logic.summary import load_formation
from utils import import_fonts
from vizzes.pitch import Pitch as PitchPreset

# Globally import the Roboto fonts for use in the plots
robotoRegular, robotoLight, robotoBold = import_fonts(which="roboto", weight="all")

# Set default font sizes
robotoRegular.set_size(7.5)
robotoLight.set_size(7.5)
robotoBold.set_size(7.5)

# ---------------------------------------------------------------------------
# Private helpers and variables

# Bbox style for goal annotation text boxes
_GOAL_LABEL_PROPS = {
    "boxstyle": "round",
    "facecolor": "white",
    "edgecolor": "black",  # overridden per-goal at draw time
    "alpha": 0.8,
}


def _scatter_shots(
    pitch, ax, shots: list, fill: str, edge: str, flip: bool = False
) -> dict:
    """
    Scatter shot events onto a pitch axis.

    Args:
        pitch: mplsoccer Pitch or VerticalPitch instance.
        ax: Matplotlib axes to draw on.
        shots (list[dict]): Shot dicts from load_shots().
        fill (str): Marker fill color.
        edge (str): Marker edge color (falls back to "black" if empty).
        flip (bool): Mirror coordinates around the pitch centre (for combined horizontal map).

    Returns:
        dict: Outcome counts — goals, on_target, post, blocked, off_target.
    """
    _MARKERS = {16: "o", 17: "o", 15: "^", 14: "s", 12: "D"}
    counts = {"goals": 0, "on_target": 0, "post": 0, "blocked": 0, "off_target": 0}
    edge_color = edge or "black"

    for shot in shots:
        x, y = float(shot["x"]), float(shot["y"])
        if flip:
            # Mirror around the pitch centre so home attacks the left goal
            x = x - (x - 50.1) * 2
            y = y - (y - 49.9) * 2

        t = shot["shot_type"]
        if t in (16, 17):
            counts["goals"] += 1
            counts["on_target"] += 1
        elif t == 15:
            counts["on_target"] += 1
        elif t == 14:
            counts["post"] += 1
        elif t == 12:
            counts["blocked"] += 1
        else:
            counts["off_target"] += 1

        pitch.scatter(
            x,
            y,
            s=max(700 * float(shot["xg"]), 30),
            marker=_MARKERS.get(t, "X"),
            color=fill,
            edgecolors=edge_color,
            linewidth=0.8,
            zorder=2,
            ax=ax,
        )

    return counts


def _pen_str(n: int) -> str:
    return f"{n} {'pen' if n <= 1 else 'pens'}"


def _npxg_label(name: str, npxg: float, pens: int) -> str:
    stat_line = f"{npxg:.2f} npxG + {_pen_str(pens)}"
    return f"{name}\n{stat_line}" if name else stat_line


def _draw_xg_steps(
    ax, xg_data, color: str, col: str, last_shot: float, graph_end: float
) -> float:
    """Draw cumulative xG step line + trailing flat to graph_end. Returns final value."""
    ax.step(
        x="minute",
        y=col,
        data=xg_data,
        color=color,
        linewidth=2.5,
        where="post",
        zorder=3,
    )
    final = float(xg_data[col].iloc[-1])
    ax.step(
        x=[last_shot, graph_end],
        y=[final, final],
        color=color,
        linewidth=2.5,
        where="post",
        zorder=3,
    )
    return final


def _annotate_goal(ax, row, color: str, edge: str, y_offset: float, bold_font) -> None:
    """Draw scatter marker + text box annotation for a single goal/own-goal row."""
    is_home = row["home_scorer"] != ""
    scorer = row["home_scorer"] if is_home else row["away_scorer"]
    y_val = float(row["home_xg"] if is_home else row["away_xg"])
    xg_val = float(row["home_xg_shot"] if is_home else row["away_xg_shot"])
    xgot_val = float(row["home_xgot"] if is_home else row["away_xgot"])

    if row["shot_type"] == 16:
        label = f"{scorer}{' (pen)' if row['is_penalty'] else ''}\n{xg_val:.2f} xG\n{xgot_val:.2f} xGOT"
    else:
        label = scorer

    ax.scatter(
        row["minute"],
        y_val,
        s=60,
        facecolors=color,
        edgecolors=edge,
        zorder=6,
        linewidth=2,
    )
    ax.text(
        row["minute"],
        y_val + y_offset,
        label,
        ha="center",
        color=color,
        zorder=6,
        fontproperties=bold_font,
        bbox={**_GOAL_LABEL_PROPS, "edgecolor": color},
        fontsize=7,
    )


def _draw_npxg_label(
    ax,
    xg_data,
    shot_col: str,
    name: str,
    final_xg: float,
    color: str,
    label_x: float,
    bold_font,
) -> None:
    """Compute npxG and draw the end-of-timeline label for one team."""
    pen_mask = xg_data["is_penalty"] & (xg_data[shot_col] > 0)
    pens = int(pen_mask.sum())
    pen_xg = float(xg_data.loc[pen_mask, shot_col].sum())
    ax.text(
        label_x,
        final_xg,
        _npxg_label(name, final_xg - pen_xg, pens),
        color=color,
        fontproperties=bold_font,
        fontsize=9,
        ha="left",
        va="center",
        zorder=6,
    )


def _draw_boundary_spans(ax, boundary_pairs: list, graph_end: float) -> None:
    """Draw opaque gap spans and period boundary lines, plus the end-of-match reference."""
    for start, end in boundary_pairs:
        ax.axvspan(start, end, facecolor="white", alpha=1.0, zorder=4)
        ax.axvline(start, color="grey", linestyle="-", alpha=0.6, zorder=5)
        ax.axvline(end, color="grey", linestyle="-", alpha=0.6, zorder=5)
    ax.axvline(graph_end, color="grey", linestyle="--", alpha=0.4, zorder=5)


def _draw_period_labels(
    ax, boundary_pairs: list, graph_end: float, is_et: bool, label_y: float, bold_font
) -> None:
    """Draw period name labels centred above each period region."""
    period_names = ["First half", "Second half"]
    if is_et:
        period_names += ["First ET", "Second ET"]
    period_starts = [0] + [end for _, end in boundary_pairs]
    period_ends = [start for start, _ in boundary_pairs] + [graph_end]
    for idx, (start, end) in enumerate(zip(period_starts, period_ends)):
        if idx >= len(period_names):
            break
        ax.text(
            (start + end) / 2,
            label_y,
            period_names[idx],
            fontproperties=bold_font,
            fontsize=9,
            ha="center",
            va="bottom",
        )


# ---------------------------------------------------------------------------
# Public plotting functions


# Plot formations
def plot_formation(
    stats_path: str,
    side: str = "home",
    pitch_type: str = "opta",
    vertical: bool = False,
) -> plt.Figure:
    """
    Plot a football formation using mplsoccer.

    Args:
        stats_path (str): Path to the stats JSON file.
        side (str): "home" or "away" to specify which team's formation to plot. Default is "home".
        pitch_type (str):
            - The type of pitch to use.
            - Default is "opta".
            - Options include "opta", "statsbomb", "tracab", etc.
        vertical (bool): Whether to plot the pitch vertically. Default is False (horizontal).

    Returns:
        plt.Figure: The matplotlib figure containing the formation plot.
    """
    # Load formation info
    formation = load_formation(stats_path, side)
    if not formation:
        raise ValueError(f"No formation data found for side '{side}' in stats file.")

    # Extract all necessary info for plotting
    formation_name = formation.get("formation", "")
    kit_colors = formation.get("kit", {"colour1": "#FFFFFF", "colour2": "#000000"})
    formation_positions = [
        player_info["formationPlace"] for player_info in formation["players"].values()
    ]
    player_text = [
        player_info.get("matchName", "")
        for player_info in formation["players"].values()
    ]
    player_numbers = [
        player_info.get("shirtNumber", "")
        for player_info in formation["players"].values()
    ]

    # Use a per-call font copy so the global object is never mutated
    font_size = 6 if vertical else 7.5
    regular_font = copy.copy(robotoRegular)
    regular_font.set_size(font_size)

    bold_font = copy.copy(robotoBold)
    bold_font.set_size(font_size)

    pitch, fig, ax = PitchPreset(
        vertical=vertical,
        pitch_type=pitch_type,
        goal_type="line",
        goal_alpha=0.2,
        pad_top=1,
        pad_bottom=1,
        pad_left=1,
        pad_right=1,
    ).draw(figsize=(6, 4))
    fig.tight_layout(pad=0)

    # Plot the player names
    pitch.formation(
        formation=formation_name,
        positions=formation_positions,
        kind="text",
        text=player_text,
        va="center",
        ha="center",
        fontproperties=regular_font,
        xoffset=-4 if vertical else 0,
        yoffset=-6 if not vertical else 0,
        ax=ax,
    )

    # Plot the scatter points for the players
    pitch.formation(
        formation=formation_name,
        positions=formation_positions,
        kind="scatter",
        color=kit_colors["colour1"],
        edgecolor=kit_colors["colour2"] if kit_colors["colour2"] else "black",
        s=200 if not vertical else 120,
        linewidth=0.9,
        ax=ax,
    )

    # Plot the shirt numbers on top of the scatter points
    pitch.formation(
        formation=formation_name,
        positions=formation_positions,
        kind="text",
        text=player_numbers,
        va="center",
        ha="center",
        fontproperties=bold_font,
        color=kit_colors["colour2"] if kit_colors["colour2"] else "black",
        xoffset=-0.1 if vertical else 0,
        yoffset=-0.3 if not vertical else -0.05,
        ax=ax,
    )

    fig.set_facecolor("none")  # Set figure background to transparent
    ax.set_facecolor("none")  # Set axes background to transparent

    return fig


def plot_xg_timeline(
    xg_data,
    axis_configs: dict,
    home_kit: dict,
    away_kit: dict,
    home_name: str = "",
    away_name: str = "",
) -> plt.Figure:
    """
    Plot a cumulative xG timeline using data from load_xg_timeline and load_axis_configs.

    Args:
        xg_data (pd.DataFrame): DataFrame returned by load_xg_timeline().
        axis_configs (dict): Dict returned by load_axis_configs().
        home_kit (dict): Home kit colors, e.g. {"colour1": "#hex", "colour2": "#hex"}.
        away_kit (dict): Away kit colors.
        home_name (str): Home team name shown on the npxG summary label.
        away_name (str): Away team name shown on the npxG summary label.

    Returns:
        plt.Figure: The matplotlib figure containing the xG timeline.
    """
    home_color = home_kit["colour1"]
    home_edge = home_kit.get("colour2") or "black"
    away_color = away_kit["colour1"]
    away_edge = away_kit.get("colour2") or "black"

    max_xg = axis_configs["max_xg"]
    graph_end = axis_configs["graph_end_time"]
    last_shot = axis_configs["last_shot"]
    is_et = axis_configs["is_extra_time"]
    boundary_pairs = axis_configs["boundary_pairs"]

    bold_font = copy.copy(robotoBold)
    bold_font.set_size(9)
    regular_font = copy.copy(robotoRegular)
    regular_font.set_size(9)

    fig, ax = plt.subplots(figsize=(12, 5))
    plt.box(False)
    fig.set_facecolor("none")
    ax.set_facecolor("none")

    # Axis limits, ticks and labels
    total_xlim = graph_end + 18
    ax.set_xlim(0, total_xlim)
    ax.set_ylim(0, max_xg * 1.05)
    plt.xticks(
        axis_configs["x_times"], axis_configs["x_labels"], fontproperties=regular_font
    )
    plt.yticks(
        axis_configs["y_times"], axis_configs["y_labels"], fontproperties=regular_font
    )
    plt.ylabel("Cumulative xG", fontproperties=bold_font)
    plt.xlabel("Minutes Played", fontproperties=bold_font)
    plt.tick_params(axis="both", which="both", length=0)

    # Horizontal grid lines capped at graph_end
    grid_xmax = graph_end / total_xlim
    for y_val in axis_configs["y_times"][1:]:
        ax.axhline(
            y_val,
            xmin=0,
            xmax=grid_xmax,
            color="grey",
            alpha=0.3,
            linewidth=0.7,
            zorder=1,
        )

    # Cumulative xG step lines
    final_home_xg = _draw_xg_steps(
        ax, xg_data, home_color, "home_xg", last_shot, graph_end
    )
    final_away_xg = _draw_xg_steps(
        ax, xg_data, away_color, "away_xg", last_shot, graph_end
    )

    # Period boundary spans and lines (zorder 4/5 — occludes step lines in gap)
    _draw_boundary_spans(ax, boundary_pairs, graph_end)

    # Goal and own-goal annotations
    y_offset = max_xg * 0.04
    for _, row in xg_data.iterrows():
        if row["shot_type"] not in (16, 26) or (
            row["home_scorer"] == "" and row["away_scorer"] == ""
        ):
            continue
        is_home = row["home_scorer"] != ""
        color = home_color if is_home else away_color
        edge = home_edge if is_home else away_edge
        _annotate_goal(ax, row, color, edge, y_offset, bold_font)

    # npxG summary labels at the right edge
    label_x = graph_end + 1
    _draw_npxg_label(
        ax,
        xg_data,
        "home_xg_shot",
        home_name,
        final_home_xg,
        home_color,
        label_x,
        bold_font,
    )
    _draw_npxg_label(
        ax,
        xg_data,
        "away_xg_shot",
        away_name,
        final_away_xg,
        away_color,
        label_x,
        bold_font,
    )

    # Period labels above each period region
    _draw_period_labels(ax, boundary_pairs, graph_end, is_et, max_xg * 1.01, bold_font)

    fig.tight_layout(pad=1.5)
    return fig


def plot_shot_map(
    shots: list,
    kit: dict,
    **pitch_overrides,
) -> plt.Figure:
    """
    Plot a half-pitch shot map for a single team.

    Each shot is plotted as a scatter point on the attacking half (VerticalPitch,
    half=True) with marker shape encoding the shot outcome and marker size
    proportional to xG. Title and legend are intentionally omitted so callers
    can use HTML/Markdown in the surrounding UI instead.

    Args:
        shots (list[dict]): Shot dicts from load_shots() for one team.
        kit (dict): Kit colors, e.g. {"colour1": "#hex", "colour2": "#hex"}.
        **pitch_overrides: Optional mplsoccer VerticalPitch kwargs merged into
            the shot-map defaults, e.g. ``pitch_color="grass", stripe=True``.

    Returns:
        plt.Figure: The matplotlib figure containing the shot map.
    """
    fill = kit["colour1"]
    edge = kit.get("colour2") or "white"

    pitch, fig, ax = PitchPreset(
        pitch_type="opta",
        half=True,
        **pitch_overrides,
    ).draw(figsize=(5, 4))
    _scatter_shots(pitch, ax, shots, fill, edge, flip=False)

    fig.patch.set_facecolor("none")
    fig.tight_layout(pad=0.5)
    return fig


# Colormap for pass-network arrows: muted periwinkle → vivid indigo → deep violet.
# Low-value arrows are pale and recede; high-value pairs saturate to deep violet
# which stands out clearly against the app's cool blue background (#9abddc).
_PASS_CMAP = LinearSegmentedColormap.from_list(
    "pass_cmap", ["#a5b4fc", "#6366f1", "#4c1d95"]
)


def plot_pass_network(network: dict, kit: dict, **pitch_overrides) -> plt.Figure:
    """
    Plot a passing network for a single team's starting XI.

    Arrows between players are scaled in width and opacity by the number of
    pass combinations. Node size reflects each player's accurate pass count.
    The figure is transparent so it inherits the surrounding container background.

    Args:
        network (dict): Dict returned by load_pass_network(), containing
            ``players`` (list of position/accuracy dicts) and ``passes``
            (list of passer→receiver combination dicts).
        kit (dict): Kit colors, e.g. {"colour1": "#hex", "colour2": "#hex"}.
        **pitch_overrides: Optional mplsoccer VerticalPitch kwargs merged into
            the pass-network defaults, e.g. ``line_alpha=0.6``.

    Returns:
        plt.Figure: The matplotlib figure containing the pass network.
    """
    fill_color = kit["colour1"]
    edge_color = kit.get("colour2") or "white"

    pitch, fig, ax = PitchPreset(
        pitch_type="opta",
        **pitch_overrides,
    ).draw(figsize=(5, 6))
    fig.set_facecolor("none")
    ax.set_facecolor("none")

    players = network["players"]
    passes = network["passes"]

    player_lookup = {p["player_id"]: p for p in players}

    # Scale arrows continuously against the max combination count
    values = [p["value"] for p in passes]
    max_val = max(values) if values else 1

    label_font = copy.copy(robotoRegular)
    label_font.set_size(7)

    # Draw arrows first (below nodes)
    for p in passes:
        if p["from_id"] not in player_lookup or p["to_id"] not in player_lookup:
            continue
        val = p["value"]
        if val < 3:
            continue
        src = player_lookup[p["from_id"]]
        dst = player_lookup[p["to_id"]]

        t = val / max_val  # 0..1
        width = 1.5 + t * 4.5
        rgba = (*_PASS_CMAP(t)[:3], 0.03 + t * 0.87)

        pitch.arrows(
            src["x"],
            src["y"],
            dst["x"],
            dst["y"],
            width=width,
            headwidth=4,
            headlength=2,
            headaxislength=2,
            color=rgba,
            ax=ax,
            zorder=2,
        )

    # Draw nodes and labels on top.
    # With VerticalPitch, x maps to the vertical axis so the label offset
    # is applied to x (not y) to position text above each node.
    for p in players:
        pitch.scatter(
            p["x"],
            p["y"],
            s=max(60, p["pass_success"] * 5),
            color=fill_color,
            edgecolors=edge_color,
            linewidths=1.5,
            zorder=3,
            ax=ax,
        )
        pitch.annotate(
            p["name"],
            (p["x"], p["y"]),
            (p["x"] + 4, p["y"]),
            ha="center",
            va="bottom",
            fontproperties=label_font,
            fontsize=7.5,
            color="black",
            ax=ax,
            zorder=4,
        )

    # Attacking direction indicator — bottom-left corner, pointing upward
    ax.annotate(
        "",
        xy=(0.06, 0.18),
        xytext=(0.06, 0.04),
        xycoords="axes fraction",
        textcoords="axes fraction",
        arrowprops={
            "arrowstyle": "-|>",
            "color": "grey",
            "lw": 1.2,
        },
        zorder=6,
    )
    ax.text(
        0.015,
        0.17,
        "Attacking direction",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontproperties=label_font,
        fontsize=6.5,
        color="grey",
        rotation=90,
        zorder=6,
    )

    fig.tight_layout(pad=0)

    return fig


def plot_possession_heatmap(
    touches: dict,
    home_kit: dict,
    away_kit: dict,
) -> plt.Figure:
    """
    Plot a full-pitch diverging possession dominance heatmap.

    Each grid cell is coloured on a continuous scale between the away colour
    (away dominant) and the home colour (home dominant), with a neutral grey
    midpoint where possession is even.  Cells where neither team reaches the
    55% dominance threshold, or with no touches from either team, are set to
    the neutral midpoint.

    Args:
        touches (dict): Dict from load_possession_versus(), containing
            ``"home"`` and ``"away"`` keys each with ``"x"``/``"y"`` lists.
        home_kit (dict): Home kit colours, e.g. {"colour1": "#hex", "colour2": "#hex"}.
        away_kit (dict): Away kit colours.

    Returns:
        plt.Figure: The matplotlib figure containing the heatmap.
    """
    home_color = home_kit["colour1"]
    away_color = away_kit["colour1"]

    cmap = LinearSegmentedColormap.from_list("dom", [away_color, "#d1e5f4", home_color])

    pitch, fig, ax = PitchPreset(
        vertical=False,
        pitch_type="opta",
    ).draw(figsize=(8, 5))
    fig.set_facecolor("none")
    ax.set_facecolor("none")

    home_xs = touches["home"]["x"]
    home_ys = touches["home"]["y"]
    away_xs = touches["away"]["x"]
    away_ys = touches["away"]["y"]

    # Bin touches into a grid for each team using the same bin edges
    bin_home = pitch.bin_statistic(home_xs, home_ys, statistic="count", bins=(6, 5))
    bin_away = pitch.bin_statistic(away_xs, away_ys, statistic="count", bins=(6, 5))

    home_counts = bin_home["statistic"].astype(float)
    away_counts = bin_away["statistic"].astype(float)
    total = home_counts + away_counts

    # Ratio: 1.0 = fully home, 0.0 = fully away, 0.5 = neutral
    # np.divide with `where` skips zero-denominator cells to avoid RuntimeWarning
    ratio = np.full_like(total, 0.5)
    np.divide(home_counts, total, out=ratio, where=total > 0)
    # Snap cells where neither team reaches the 55% dominance threshold to neutral
    ratio = np.where((ratio > 0.45) & (ratio < 0.55), 0.5, ratio)

    # Render via the home bin_statistic structure (shares bin edges/grid)
    bin_home["statistic"] = ratio
    pitch.heatmap(
        bin_home, ax=ax, cmap=cmap, vmin=0, vmax=1, edgecolors="none", alpha=0.75
    )

    fig.tight_layout(pad=0.5)
    return fig
