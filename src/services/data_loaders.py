# Data loading functions for different data sources

# Imports
import streamlit as st


def render_opta_wyscout_inputs():
    """
    Render input widgets for Opta/Wyscout data sources.

    Returns:
        list: Uploaded files (if file upload selected), or empty list.
    """
    uploaded_files = []

    source_type = st.radio(
        "File source:",
        options=["From API", "File Upload"],
        index=1,
        key="opta_source",
        horizontal=True,
    )

    if source_type == "From API":
        match_id = st.text_input(
            label="Enter match ID:",
            placeholder="e.g. 1234567",
            key="match_id",
        )
        if st.button("Fetch", key="fetch_api"):
            with st.spinner(f"Fetching match {match_id} from API..."):
                st.warning("Not ready yet.")
    else:  # File Upload
        uploaded_files = st.file_uploader(
            "Upload Opta/Wyscout file:",
            accept_multiple_files=True,
            type=["json"],
            key="opwy_upload",
        )

    return uploaded_files


def render_statsbomb_skillcorner_inputs(data_source: str):
    """
    Render input widgets for StatsBomb/SkillCorner data sources.

    Args:
        data_source (str): The data source name.

    Returns:
        str: Selected source type ("Open Data" or "File Upload").
    """
    source_type = st.radio(
        "File source:",
        options=["Open Data", "File Upload"],
        index=0,
        key=f"{data_source.lower()}_source",
        horizontal=True,
    )

    if source_type == "Open Data":
        pass
    else:  # File Upload
        uploaded_files = st.file_uploader(
            f"Upload {data_source} file(s):",
            accept_multiple_files=True,
            type=["json", "csv"],
            key=f"{data_source.lower()}_upload",
        )

    return uploaded_files if source_type == "File Upload" else source_type


def render_blend_inputs(data_sources: list):
    """
    Render input widgets for Blend data source.

    Args:
        data_sources (list): List of available data sources.

    Returns:
        list: Selected data sources for blending.
    """
    selected_sources = st.pills(
        "Select two or more data sources:",
        options=data_sources[:-2],  # Exclude "Blend" and "Other"
        selection_mode="multi",
    )

    if len(selected_sources) < 2:
        st.warning("Please select at least two data sources to blend.")

    for source in selected_sources:
        st.markdown(f"**Source: {source}**")
        if source in ["Opta", "Wyscout"]:
            uploaded_files = render_opta_wyscout_inputs()
        elif source in ["StatsBomb", "SkillCorner"]:
            source_type = render_statsbomb_skillcorner_inputs(source)

    return selected_sources


def render_other_inputs():
    """
    Render input widgets for Other data source.

    Returns:
        str: Custom data source name entered by user.
    """
    other_source = st.text_input(
        label="Enter data source name:",
        placeholder="e.g. CSV, JSON, etc.",
        key="other_data",
    )

    return other_source
