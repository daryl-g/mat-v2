# CSS-imitated code for styling the Streamlit app

# Import necessary libraries
import streamlit as st
import os
import base64

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

        /* Tab styling with borders and glow */
        {self.st_tab(style_dict)}

        /* Warning and error message styling */
        {self.st_error_warning(style_dict)}

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
            "alt-text-color": "#3c3e40",
            "primary-color": "#9abddc",
            "title-color": "#3c3e40",
            "alt-title-color": "#e5f3fd",
            "border-color": "#f5fbff",
            "alt-border-color": "#3c3e40",
            "dark-navy": "#2c5f8d",
            "dark-green": "#2d7a4f",
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
            padding-top: 3rem;
        }
        [data-testid="stHeader"] {
            height: 3rem;
            min-height: 3rem;
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
        gradient = "linear-gradient(to bottom, #9abddc, #f5fbff)"

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
                        background: {gradient};
                    }}
                """
        else:
            # Fallback to gradient only
            return f"""
                .stApp, [data-testid="stHeader"] {{
                    background-image: {gradient};
                }}
            """

    # Tab container styling
    def st_tab(self, style_dict: dict) -> str:
        """
        Style Streamlit tabs with borders and background for active tab.

        Args:
            style_dict (dict): Dictionary with colour palette.
        Returns:
            str: CSS styles for tabs.
        """
        dark_navy = style_dict.get("dark-navy", "#2c5f8d")
        title_color = style_dict.get("title-color", "#3c3e40")
        text_color = style_dict.get("text-color", "#f5fbff")
        alt_title_color = style_dict.get("alt-title-color", "#e5f3fd")
        alt_border_color = style_dict.get("alt-border-color", "#3c3e40")

        return f"""
        /* Tab container scrollbar styling */
        /*
        div[data-baseweb="tab-list"] {{
            scrollbar-width: thin;
            scrollbar-color: {dark_navy};
        }}
        
        div[data-baseweb="tab-list"]::-webkit-scrollbar {{
            height: 10px;
        }}
        
        div[data-baseweb="tab-list"]::-webkit-scrollbar-button {{
            display: none;
        }}
        
        div[data-baseweb="tab-list"]::-webkit-scrollbar-track {{
            background: transparent;
        }}
        
        div[data-baseweb="tab-list"]::-webkit-scrollbar-thumb {{
            background-color: {dark_navy};
            border-radius: 5px;
            border: 1px solid {text_color}33;
        }}
        
        div[data-baseweb="tab-list"]::-webkit-scrollbar-thumb:hover {{
            background-color: {dark_navy}DD;
            border-color: {text_color}66;
        }}
        */
        
        /* Tab button styling */
        button[data-baseweb="tab"] {{
            border-bottom: 2px solid {dark_navy};
            border-radius: 8px 8px 0 0;
            padding: 0.5rem 1.5rem;
            background-color: {dark_navy}33;
            transition: all 0.3s ease;
            color: {title_color};
        }}
        
        /* Active tab styling with background */
        button[data-baseweb="tab"][aria-selected="true"] {{
            border-bottom: 2px solid {"#c9022d"};
            background-color: {"#f51848"}80;
            box-shadow: 0 6px 2px -2px {"#c9022d"};
            color: {text_color};
        }}
        
        /* Hover effect for non-active tabs */
        button[data-baseweb="tab"]:hover:not([aria-selected="true"]) {{
            background-color: {dark_navy}80;
            color: {alt_title_color};
        }}
        
        /* Tab panel content area styling */
        div[role="tabpanel"] {{
            border: 1px solid {alt_border_color}33;
            border-top: none;
            border-radius: 0 0 8px 8px;
            padding: 1rem;
        }}
        """

    # Warning/Error message styling
    def st_error_warning(self, style_dict: dict) -> str:
        """
        Style Streamlit warning and error messages.

        Args:
            style_dict (dict): Dictionary with colour palette.
        Returns:
            str: CSS styles for warnings and errors.
        """
        alt_text_color = style_dict.get("alt-text-color", "#3c3e40")

        return f"""
        /* Warning message styling */
        [data-testid="stAlertContentWarning"] {{
            color: #878700;
        }}
        /* Error message styling */
        [data-testid="stAlertContentError"] {{
            color: #870000;
        }}
        """
