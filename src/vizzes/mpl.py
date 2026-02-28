# Static vizzes using matplotlib and mplsoccer

# Imports
import copy
import matplotlib.pyplot as plt

from mplsoccer import Pitch, VerticalPitch

# Custom modules
from logic.summary import load_formation
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
