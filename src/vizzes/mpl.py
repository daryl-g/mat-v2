# Static vizzes using matplotlib and mplsoccer

# Imports
import copy
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from mplsoccer import Pitch, VerticalPitch

# Custom modules
from logic.summary import load_formation
from logic.xgoal import PEN_XG as _PEN_XG
from utils import import_fonts

# Globally import the Roboto fonts for use in the plots
robotoRegular, robotoLight, robotoBold = import_fonts(which="roboto", weight="all")

# Set default font sizes
robotoRegular.set_size(7.5)
robotoLight.set_size(7.5)
robotoBold.set_size(7.5)


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

    # Set up the pitch
    pitch_line_color = "#635959"
    pitch_line_alpha = 0.2
    pitch_line_width = 1
    if vertical:
        pitch = VerticalPitch(
            pitch_type=pitch_type,
            goal_type="line",
            goal_alpha=pitch_line_alpha,
            line_color=pitch_line_color,
            line_alpha=pitch_line_alpha,
            linewidth=pitch_line_width,
            pad_top=1,
            pad_bottom=1,
            pad_left=1,
            pad_right=1,
        )
    else:
        pitch = Pitch(
            pitch_type=pitch_type,
            goal_type="line",
            goal_alpha=pitch_line_alpha,
            line_color=pitch_line_color,
            line_alpha=pitch_line_alpha,
            linewidth=pitch_line_width,
            pad_top=1,
            pad_bottom=1,
            pad_left=1,
            pad_right=1,
        )

    # Use a per-call font copy so the global object is never mutated
    font_size = 6 if vertical else 7.5
    regular_font = copy.copy(robotoRegular)
    regular_font.set_size(font_size)

    bold_font = copy.copy(robotoBold)
    bold_font.set_size(font_size)

    fig, ax = pitch.draw(figsize=(6, 4))
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


# ---------------------------------------------------------------------------
# Private helpers


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


# ---------------------------------------------------------------------------
# Public plotting functions


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

    # Set axis limits first — xlim needed so grid fraction is correct
    total_xlim = graph_end + 18
    ax.set_xlim(0, total_xlim)
    ax.set_ylim(0, max_xg * 1.05)

    # Axis ticks and labels
    plt.xticks(
        axis_configs["x_times"], axis_configs["x_labels"], fontproperties=regular_font
    )
    plt.yticks(
        axis_configs["y_times"], axis_configs["y_labels"], fontproperties=regular_font
    )
    plt.ylabel("Cumulative xG", fontproperties=bold_font)
    plt.xlabel("Minutes Played", fontproperties=bold_font)
    plt.tick_params(axis="both", which="both", length=0)

    # Horizontal grid lines capped at graph_end (no bleed into the label area)
    grid_xmax = graph_end / total_xlim
    for y_val in axis_configs["y_times"][1:]:  # skip the 0 baseline
        ax.axhline(
            y_val,
            xmin=0,
            xmax=grid_xmax,
            color="grey",
            alpha=0.3,
            linewidth=0.7,
            zorder=1,
        )

    # Cumulative xG step lines (zorder 3 — below the boundary spans)
    ax.step(
        x="minute",
        y="home_xg",
        data=xg_data,
        color=home_color,
        linewidth=2.5,
        where="post",
        zorder=3,
    )
    ax.step(
        x="minute",
        y="away_xg",
        data=xg_data,
        color=away_color,
        linewidth=2.5,
        where="post",
        zorder=3,
    )
    final_home_xg = float(xg_data["home_xg"].iloc[-1])
    final_away_xg = float(xg_data["away_xg"].iloc[-1])
    ax.step(
        x=[last_shot, graph_end],
        y=[final_home_xg, final_home_xg],
        color=home_color,
        linewidth=2.5,
        where="post",
        zorder=3,
    )
    ax.step(
        x=[last_shot, graph_end],
        y=[final_away_xg, final_away_xg],
        color=away_color,
        linewidth=2.5,
        where="post",
        zorder=3,
    )

    # Period boundary spans and lines drawn AFTER the step lines (zorder 4/5).
    # Opaque white fill fully occludes the step lines in the gap region.
    for start, end in boundary_pairs:
        ax.axvspan(start, end, facecolor="white", alpha=1.0, zorder=4)
        ax.axvline(start, color="grey", linestyle="-", alpha=0.6, zorder=5)
        ax.axvline(end, color="grey", linestyle="-", alpha=0.6, zorder=5)

    # End-of-match reference line
    ax.axvline(graph_end, color="grey", linestyle="--", alpha=0.4, zorder=5)

    # Goal and own-goal annotations
    y_offset = max_xg * 0.04
    for _, row in xg_data.iterrows():
        if row["shot_type"] not in (16, 26) or (
            row["home_scorer"] == "" and row["away_scorer"] == ""
        ):
            continue

        is_home_goal = row["home_scorer"] != ""
        scorer = row["home_scorer"] if is_home_goal else row["away_scorer"]
        color = home_color if is_home_goal else away_color
        edge_c = home_edge if is_home_goal else away_edge
        y_val = float(row["home_xg"]) if is_home_goal else float(row["away_xg"])
        xg_val = (
            float(row["home_xg_shot"]) if is_home_goal else float(row["away_xg_shot"])
        )
        xgot_val = float(row["home_xgot"]) if is_home_goal else float(row["away_xgot"])

        if row["shot_type"] == 16:
            is_pen = abs(xg_val - _PEN_XG) < 0.001
            label = f"{scorer}{' (pen)' if is_pen else ''}\n{xg_val:.2f} xG \n{xgot_val:.2f} xGOT"
        else:
            label = scorer

        props = dict(boxstyle="round", facecolor="white", edgecolor=color, alpha=0.8)
        ax.scatter(
            row["minute"],
            y_val,
            s=60,
            facecolors=color,
            edgecolors=edge_c,
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
            bbox=props,
            fontsize=7,
        )

    # npxG summary labels at the right edge, with team names
    home_pens = int(((xg_data["home_xg_shot"] - _PEN_XG).abs() < 0.001).sum())
    away_pens = int(((xg_data["away_xg_shot"] - _PEN_XG).abs() < 0.001).sum())

    def _pen_str(n):
        return f"{n} {'pen' if n <= 1 else 'pens'}"

    home_npxg = final_home_xg - home_pens * _PEN_XG
    away_npxg = final_away_xg - away_pens * _PEN_XG

    def _label(name: str, npxg: float, pens: int) -> str:
        stat_line = f"{npxg:.2f} npxG + {_pen_str(pens)}"
        return f"{name}\n{stat_line}" if name else stat_line

    label_x = graph_end + 1
    ax.text(
        label_x,
        final_home_xg,
        _label(home_name, home_npxg, home_pens),
        color=home_color,
        fontproperties=bold_font,
        fontsize=9,
        ha="left",
        va="center",
        zorder=6,
    )
    ax.text(
        label_x,
        final_away_xg,
        _label(away_name, away_npxg, away_pens),
        color=away_color,
        fontproperties=bold_font,
        fontsize=9,
        ha="left",
        va="center",
        zorder=6,
    )

    # Period labels just inside the top of each period region
    period_names = ["First half", "Second half"]
    if is_et:
        period_names += ["First ET", "Second ET"]

    period_starts = [0] + [end for _, end in boundary_pairs]
    period_ends = [start for start, _ in boundary_pairs] + [graph_end]
    label_y = max_xg * 1.01
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

    fig.tight_layout(pad=1.5)
    return fig


def plot_shot_map(
    shots: list,
    kit: dict,
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

    Returns:
        plt.Figure: The matplotlib figure containing the shot map.
    """
    fill = kit["colour1"]
    edge = kit.get("colour2") or "white"

    pitch = VerticalPitch(
        pitch_type="opta",
        half=True,
        pitch_color="grass",
        line_color="white",
        stripe=True,
    )
    fig, ax = pitch.draw(figsize=(5, 4))
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


def plot_pass_network(network: dict, kit: dict) -> plt.Figure:
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

    Returns:
        plt.Figure: The matplotlib figure containing the pass network.
    """
    fill_color = kit["colour1"]
    edge_color = kit.get("colour2") or "white"

    pitch = VerticalPitch(
        pitch_type="opta",
        pitch_color="none",
        line_color="grey",
        line_alpha=0.4,
        linewidth=1,
    )
    fig, ax = pitch.draw(figsize=(5, 6))
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
        arrowprops=dict(arrowstyle="-|>", color="grey", lw=1.2),
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
