# Reusable title component for pages

# Imports
import streamlit as st
from utils import load_image


def page_title(
    title_text: str,
    is_home: bool = False,
    palette: dict = None,
) -> None:
    """
    Render a page title with logo. Centered and large on home page,
    top-left in header on other pages.

    Args:
        title_text (str): The title text to display.
        is_home (bool): Whether this is the home page. Default is False.
        palette (dict): Color palette dictionary. Default is None.
    """
    if palette is None:
        palette = {"title-color": "#3c3e40", "alt-title-color": "#e5f3fd"}

    # Select logo based on page type
    logo_path = (
        "assets/logos/mat_logo_dark.png"
        if is_home
        else "assets/logos/mat_logo_light.png"
    )

    try:
        logo_b64 = load_image(logo_path)
    except Exception as e:
        st.error(f"Error loading logo: {e}")
        logo_b64 = None

    if is_home:
        # Home page: Centered, large, static
        st.html(
            f"""
            <style>
                .title-home {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 2rem 0;
                }}
                .title-home-content {{
                    display: flex;
                    align-items: center;
                }}
            </style>
            <div class="title-home">
                <div class="title-home-content">
                    {f"<img src='{logo_b64}' style='width: 5.5rem; height: 5.5rem;' />" if logo_b64 else ""}
                    <h1 style='font-size: 3.5em; color: {palette['title-color']}; font-weight: bold; margin: 0; margin-left: 1.5rem;'>
                        {title_text}
                    </h1>
                </div>
            </div>
            """
        )
    else:
        # Other pages: Use HTML + CSS to show title at the top left in the header
        st.html(
            f"""
            <style>
                .page-title-header {{
                    width: fit-content;
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                }}
                
                .page-title-logo {{
                    width: 2.8rem;
                    height: 2.8rem;
                }}
                
                .page-title-text {{
                    font-size: 1.3em;
                    color: {palette.get('alt-title-color', '#e5f3fd')};
                    font-weight: bold;
                    margin: 0;
                }}
            </style>
            
            <a href="/" style="text-decoration: none; width: fit-content; display: inline-block;">
                <div class="page-title-header">
                    {f"<img src='{logo_b64}' class='page-title-logo' alt='Logo' />" if logo_b64 else ""}
                    <span class="page-title-text">{title_text}</span>
                </div>
            </a>
            """
        )
