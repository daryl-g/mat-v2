# Initialise and draw a pitch with Plotly and mplsoccer
# TODO: Eventually merge this with the mplsoccer pitch class to avoid code duplication and maintenance issues.

# Imports
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from typing import Literal
from mplsoccer import Pitch as MplPitch, VerticalPitch as MplVerticalPitch


class Pitch:
    """
    Class to draw an mplsoccer pitch with arbitrary configuration.

    Pass any keyword argument accepted by mplsoccer's ``Pitch`` or
    ``VerticalPitch`` directly to the constructor; they are forwarded verbatim
    when ``draw()`` is called.  This keeps a single, flexible entry-point
    instead of per-use-case factory methods.

    Example::

        pitch, fig, ax = Pitch(
            pitch_type="opta",
            half=True,
        ).draw(figsize=(5, 4))
    """

    def __init__(
        self,
        lib: Literal["plotly", "mpl"] = "mpl",
        vertical: bool = True,
        pitch_color: str = "none",
        line_color: str = "grey",
        line_alpha: float = 0.5,
        linewidth: int | float = 1,
        **pitch_kwargs,
    ):
        """
        Args:
            lib (str): Rendering backend — ``"mpl"`` (mplsoccer) or ``"plotly"``.
                Default is ``"mpl"``.
            vertical (bool): Use ``VerticalPitch`` when True, ``Pitch`` when
                False. Default is True.
            pitch_color (str): Pitch background colour. Default is ``"none"``
                (transparent) so the figure inherits the surrounding container
                background.
            line_color (str): Pitch line colour. Default is ``"grey"``.
            line_alpha (float): Pitch line opacity (0–1). Default is ``0.5``.
            linewidth (int | float): Pitch line width in points. Default is ``1``.
            **pitch_kwargs: Any remaining keyword argument accepted by
                mplsoccer's ``Pitch`` or ``VerticalPitch`` (e.g. ``pitch_type``,
                ``half``, ``stripe``, ``goal_type``, …).  ``pitch_type`` is
                intentionally left without a default so callers always supply
                it explicitly from the active data-source context.
        """
        if lib not in ("plotly", "mpl"):
            raise ValueError(
                "Unknown library. Please choose between 'plotly' and 'mpl'."
            )
        self.lib: str = lib
        self.vertical: bool = vertical
        self._pitch_kwargs: dict = {
            "pitch_color": pitch_color,
            "line_color": line_color,
            "line_alpha": line_alpha,
            "linewidth": linewidth,
            **pitch_kwargs,
        }

    def draw(self, figsize: tuple | None = None) -> tuple:
        """
        Draw the pitch and return the mplsoccer instance alongside the figure.

        Args:
            figsize (tuple | None): Optional ``(width, height)`` in inches
                forwarded to mplsoccer's draw call.

        Returns:
            tuple: ``(mpl_pitch, fig, ax)`` where ``mpl_pitch`` is the
            underlying mplsoccer object — required for calls like
            ``pitch.scatter()``, ``pitch.arrows()``, ``pitch.formation()``,
            ``pitch.annotate()``, etc.
        """
        if self.lib == "plotly":
            print("Plotly draw not yet available.")
            return None

        pitch_cls = MplVerticalPitch if self.vertical else MplPitch
        mpl_pitch = pitch_cls(**self._pitch_kwargs)
        draw_kwargs = {"figsize": figsize} if figsize is not None else {}
        fig, ax = mpl_pitch.draw(**draw_kwargs)
        return mpl_pitch, fig, ax


class PlotlyPitch:
    """
    Class to draw a pitch with Plotly.
    """

    def __init__(
        self,
        # Pitch configs
        data_source: Literal["opta", "statsbomb", "skillcorner"] = "opta",
        half_pitch: bool = False,
        pitch_bg: str = None,
        fig_height: int | float = 750,
        fig_width: int | float = 1200,
        label: bool = False,
        tick: bool = False,
        corner_arcs: bool = False,
        # Line configs
        line_color: str = "#ffffff",
        line_alpha: int | float = 1,
        line_width: int | float = 2,
        line_style: Literal[
            "solid", "dot", "dash", "longdash", "dashdot", "longdashdot"
        ] = "solid",
        # Stripe configs
        stripe: bool = False,
        stripe_color: str = "#000000",
        # Positional/Juego de Posicion configs
        positional: bool = False,
        positional_linewidth: float | None = None,
        positional_linestyle: str | None = None,
        positional_color: str = "#000000",
        positional_alpha: float = 1,
        # Goal box configs
        goal_type: str = "line",
        goal_alpha: float = 1,
        goal_linestyle: str | None = None,
    ):
        """
        Initialise the Pitch class and pass user-specified values onto child functions.

        Args:
            data_source (str): Data source to be drawn on the pitch and for modifying the pitch coordinates.
                - Options are "opta", "statsbomb", "skillcorner".
                - Default is "opta".
            pitch_bg (str): Hex/RGBA colour string for the pitch background.
            fig_height (int | float): Figure height in pixel. See: https://plotly.com/python-api-reference/generated/plotly.graph_objects.html#plotly.graph_objects.Layout.height
            fig_width (int | float): Figure width in pixel. See: https://plotly.com/python-api-reference/generated/plotly.graph_objects.html#plotly.graph_objects.Layout.width
            line_color (str): Hex/RGBA colour string for the pitch outlines. Default is `#ffffff` for white.
            line_width (int | float): Pitch border line width. Default is 2px.
            line_style (str): Pitch border line dash style.
                - Options are "solid", "dot", "dash", "longdash", "dashdot", "longdashdot"
                - Default is "solid`.
        """
        # Input checking
        if data_source in ["opta", "statsbomb", "skillcorner"]:
            self.data_source: str = data_source
            # Use the user-specified data source to set the global coordinates
            self.set_coordinates()
        else:
            raise ValueError(
                "Unknown data source. Please choose between 'opta', 'statsbomb' or 'skillcorner'."
            )

        # There should be input checking for these too, but I'm a bit lazy to do it now
        self.pitch_bg: str = pitch_bg
        self.fig_height: int | float = fig_height
        self.fig_width: int | float = fig_width
        self.line_color: str = line_color
        self.line_width: int | float = line_width
        self.line_style: str = line_style

    # Set the coordinates based on the data source
    def set_coordinates(self) -> None:
        """
        Set the min, max, and special coordinates based on the user-specified data source.

        Args:
            data_source (str): User-specified data source when initialised the Pitch class.

        Returns:
            (min_max, specials) (dict, dict): A tuple of dictionary with the coordinates for drawing the pitch.
        """
        if self.data_source is None:
            # Assume a default data source...
            self.data_source = "opta"
            # ...then trigger this function again to set the global coordinates
            self.set_coordinates()

        elif self.data_source == "opta":
            self.min_max, self.specials = (
                {"min_x": 0, "max_x": 100, "min_y": 0, "max_y": 100},
                {
                    # 6-yard box
                    "x0_6yrd": 0,
                    "x1_6yrd": 5.8,
                    "y0_6yrd": 36.8,
                    "y1_6yrd": 63.2,
                    # 18-yard box
                    "x0_18yrd": 0,
                    "x1_18yrd": 17,
                    "y0_18yrd": 21.1,
                    "y1_18yrd": 78.9,
                    # Penalty spot
                    "x1_pen": 11.5,
                    "x2_pen": 88.5,
                    "y_pen": 50,
                    # Centre spot
                    "x0_mid": 49.8,
                    "x1_mid": 50.2,
                    "y0_mid": 49.6,
                    "y1_mid": 50.4,
                    # Centre circle
                    "x0_cent": 42,
                    "x1_cent": 58,
                    "y0_cent": 36.8,
                    "y1_cent": 63.2,
                    # 5 vertical lanes
                    # 3 horizontal lanes
                },
            )

    # Draw the pitch
    def draw(self) -> go.Figure:
        """
        Draw a pitch on Plotly figure and return the figure for further customisation.
        """

        # Input checking
        if (
            (type(self.min_max) != dict)
            or (type(self.specials) != dict)
            or (self.min_max is None)
            or (self.specials is None)
        ):
            raise TypeError(
                "No coordinates set is found. Please initialise the class and specify the inputs before calling the `draw` function."
            )
        if (len(self.min_max) == 0) or (len(self.specials) == 0):
            raise ValueError(
                "Coordinates data is missing or corrupted. Please check if a data source is specified and/or manually call the `set_coordinates`."
            )

        fig = go.Figure()

        # Create a list of all shape objects
        shapes = []

        # Pitch borders
        shapes.append(
            {
                "type": "rect",
                "x0": self.min_max["min_x"],
                "y0": self.min_max["min_y"],
                "x1": self.min_max["max_x"],
                "y1": self.min_max["max_y"],
                "line": {
                    "color": self.line_color,
                    "width": self.line_width,
                    "dash": self.line_style,
                },
            }
        )

        # Halfway line
        shapes.append(
            {
                "type": "line",
                "x0": self.min_max["max_x"] / 2,
                "y0": self.min_max["min_y"],
                "x1": self.min_max["max_x"] / 2,
                "y1": self.min_max["max_y"],
                "line": {
                    "color": self.line_color,
                    "width": self.line_width,
                    "dash": self.line_style,
                },
            }
        )

        # Penalty boxes
        shapes.append(
            {
                "type": "rect",
                "x0": self.specials["x0_18yrd"],
                "y0": self.specials["y0_18yrd"],
                "x1": self.specials["x1_18yrd"],
                "y1": self.specials["y1_18yrd"],
                "line": {
                    "color": self.line_color,
                    "width": self.line_width,
                    "dash": self.line_style,
                },
            }
        )
        shapes.append(
            {
                "type": "rect",
                "x0": self.min_max["max_x"] - self.specials["x1_18yrd"],
                "y0": self.min_max["max_y"] - self.specials["y1_18yrd"],
                "x1": self.min_max["max_x"] - self.specials["x0_18yrd"],
                "y1": self.min_max["max_y"] - self.specials["y0_18yrd"],
                "line": {
                    "color": self.line_color,
                    "width": self.line_width,
                    "dash": self.line_style,
                },
            }
        )

        # Six-yard boxes
        shapes.append(
            {
                "type": "rect",
                "x0": self.specials["x0_6yrd"],
                "y0": self.specials["y0_6yrd"],
                "x1": self.specials["x1_6yrd"],
                "y1": self.specials["y1_6yrd"],
                "line": {
                    "color": self.line_color,
                    "width": self.line_width,
                    "dash": self.line_style,
                },
            }
        )
        shapes.append(
            {
                "type": "rect",
                "x0": self.min_max["max_x"] - self.specials["x1_6yrd"],
                "y0": self.min_max["max_y"] - self.specials["y1_6yrd"],
                "x1": self.min_max["max_x"] - self.specials["x0_6yrd"],
                "y1": self.min_max["max_y"] - self.specials["y0_6yrd"],
                "line": {
                    "color": self.line_color,
                    "width": self.line_width,
                    "dash": self.line_style,
                },
            }
        )

        # Centre circle
        shapes.append(
            {
                "type": "circle",
                "x0": self.specials["x0_cent"],
                "y0": self.specials["y0_cent"],
                "x1": self.specials["x1_cent"],
                "y1": self.specials["y1_cent"],
                "line": {
                    "color": self.line_color,
                    "width": self.line_width,
                    "dash": self.line_style,
                },
            }
        )
        shapes.append(
            {
                "type": "circle",
                "x0": self.specials["x0_mid"],
                "y0": self.specials["y0_mid"],
                "x1": self.specials["x1_mid"],
                "y1": self.specials["y1_mid"],
                "line": {
                    "color": self.line_color,
                    "width": self.line_width,
                    "dash": self.line_style,
                },
                "fillcolor": self.line_color,
            }
        )

        # Penalty Spots
        shapes.append(
            {
                "type": "circle",
                "x0": self.specials["x0_pen1"],
                "y0": self.specials["y0_pen"],
                "x1": self.specials["x1_pen1"],
                "y1": self.specials["y1_pen"],
                "line": {
                    "color": self.line_color,
                    "width": self.line_width,
                    "dash": self.line_style,
                },
                "fillcolor": self.line_color,
            }
        )
        shapes.append(
            {
                "type": "circle",
                "x0": self.specials["x0_pen2"],
                "y0": self.specials["y0_pen"],
                "x1": self.specials["x1_pen2"],
                "y1": self.specials["y1_pen"],
                "line": {
                    "color": self.line_color,
                    "width": self.line_width,
                    "dash": self.line_style,
                },
                "fillcolor": self.line_color,
            }
        )

        # Update the figure with all shapes
        fig.update_layout(shapes=shapes)

        # Basic Styling
        fig.update_layout(
            plot_bgcolor=self.pitch_bg,
            xaxis=dict(
                range=[self.min_max["min_x"], self.min_max["max_x"]],
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                visible=False,
            ),
            yaxis=dict(
                range=[self.min_max["min_y"], self.min_max["max_y"]],
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                visible=False,
            ),
            showlegend=False,
            width=self.fig_width,  # This and height below can become inputs for this function
            height=self.fig_height,
            # margin=dict(l=10, r=10, t=30, b=10),
        )

        return fig
