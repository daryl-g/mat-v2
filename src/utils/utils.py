# Utility functions

# Imports
import base64
import pandas as pd
import streamlit as st
import matplotlib.font_manager as fm  # Import fonts

from PIL import Image


@st.cache_data
def import_fonts(
    which: str = "roboto",
    weight: str = "regular",
) -> fm.FontProperties | list[fm.FontProperties, fm.FontProperties, fm.FontProperties]:
    """
    This function imports the Roboto Regular and/or Roboto Bold fonts from the same folder as this code.

    Args:
        which (str): Which font to import? Options are "roboto". Default is "roboto".
        weight (str): Single font weight ('regular', 'light', 'bold'). Use 'all' to get all fonts.

    Returns:
        Single font properties or tuple containing the fonts.
    """
    # Inputs checking
    if which.lower() not in ["roboto"]:
        raise ValueError("Unknown font type. Please choose between 'roboto'.")

    # Import the fonts from the same folder as this code
    robotoRegular = fm.FontProperties(fname="src/assets/fonts/Roboto-Regular.ttf")
    robotoLight = fm.FontProperties(fname="src/assets/fonts/Roboto-Light.ttf")
    robotoBold = fm.FontProperties(fname="src/assets/fonts/Roboto-Bold.ttf")

    if which == "roboto":
        if weight == "all":
            return robotoRegular, robotoLight, robotoBold
        elif weight == "regular":
            return robotoRegular
        elif weight == "light":
            return robotoLight
        elif weight == "bold":
            return robotoBold
        else:
            raise ValueError(
                "Unknown font weight. Please choose from 'regular', 'light', 'bold', or 'all' to get all fonts."
            )


@st.cache_data
def load_image(path: str, as_base64: bool = True) -> str | Image.Image:
    """
    Loads an image from the given path and optionally encodes it as a base64 string.

    Args:
        path (str): Path to the image file.
        as_base64 (bool): If True, returns base64 encoded string. If False, returns PIL Image object. Default is True.
    Returns:
        str | Image.Image: Base64 encoded image as a data URI string or PIL Image object.
    """
    if as_base64:
        with open(path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        # Determine the image type from the file extension
        extension = path.split(".")[-1].lower()
        mime_type = f"image/{extension}" if extension != "jpg" else "image/jpeg"

        return f"data:{mime_type};base64,{encoded_image}"
    else:
        return Image.open(path)


@st.cache_resource
def plotly_config() -> dict:
    """
    Just a quick function to get the configurations for the Plotly plot.

    Returns:
        dict: Dictionary with Plotly plot configs.
    """
    return {
        "scrollZoom": False,
        "responsiveness": True,
        "doubleClick": "reset+autosize",
        "displayModeBar": False,
    }
