# CSS-imitated code for styling the Streamlit app

# Import necessary libraries
import streamlit as st
import os

# Custom modules
from utils import load_image


# Class to manage the CSS styles
class Styles:

    # Class constructor
    def __init__(self):
        pass

    # Return the CSS styles
    def style_init(self, style_dict: dict):
        """
        Initialize the CSS styles for the Streamlit app.

        Args:
            style_dict (dict): Dictionary with colour palette.
        Returns:
            st.html: CSS styles as a string.
        """
        return st.html(
            f"""
        <style>

        /* Layout customisations */
        /* Reduce top padding of the main block */
        {self.main_block()}

        /* Background styling with image and gradient fallback */
        {self.background_style()}

        </style>
        """,
        )

    @st.cache_resource
    # Get a dictionary of style elements
    def get_style(_self) -> dict:
        """
        Get palette colours in a dictionary.

        Returns:
            (dict): Dictionary with colour palette elements.
        """

        return {
            "bg-color": "#9abddc",
            "secondary-bg": "#d1e5f4",
            "text-color": "#f5fbff",
            "primary-color": "#9abddc",
            "title-color": "#3c3e40",
            "border-color": "#f5fbff",
        }

    # Set the global style
    def set_style(self) -> None:
        """
        Set the global style based on the variable passed down.

        Args:
            style (str): User chosen style. Options include `light`, `dark`, `tokyo`. Default is "dark" for dark mode.

        Return:
            None: Style class receives global style variable.
        """

        style_dict: dict = self.get_style()
        self.style_init(style_dict)

    # Reduce padding of the main block container
    def main_block(self) -> str:
        return """
        .stMainBlockContainer {
            padding-top: 4.5rem;
        }
        """

    # Set background with image fallback to gradient
    def background_style(self) -> str:
        """
        Set the background style with an existing image.
        Falls back to a gradient if the image is not available.

        Returns:
            str: CSS styles for background.
        """

        bg_image_path = "assets/bg/fm_mat_bg.png"
        gradient = (
            "linear-gradient(to bottom, #9abddc, #b0cde4, #c6dced, #ddecf6, #f5fbff)"
        )

        # Check if background image exists and encode it
        if os.path.exists(bg_image_path):
            try:
                encoded_image = load_image(bg_image_path)

                # Use base64 encoded image with gradient as fallback
                return f"""
                    .stApp, [data-testid="stHeader"] {{
                        background-image:
                            url('{encoded_image}'),
                            {gradient};
                        background-size: cover;
                        background-position: center;
                        background-repeat: no-repeat;
                        background-attachment: fixed;
                    }}
                """
            except Exception:
                # If encoding fails, fallback to gradient only
                return f"""
                    .stApp, [data-testid="stHeader"] {{
                        background-image: {gradient};
                    }}
                """
        else:
            # Fallback to gradient only
            return f"""
                .stApp, [data-testid="stHeader"] {{
                    background-image: {gradient};
                }}
            """
