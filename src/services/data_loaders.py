# Data loading functions for different data sources

# Imports
import streamlit as st

from utils import load_json


def render_opta_wyscout_inputs(source: str) -> list:
    """
    Render input widgets for Opta/Wyscout data sources.

    Args:
        source (str): The data source name ("Opta" or "Wyscout").

    Returns:
        list: Uploaded files (if file upload selected), or empty list.
    """
    uploaded_files = []
    uploaded_file_names = []
    expected_opta_files = ["xgoal", "events", "passmap", "stats", "squad"]

    source_type = st.radio(
        "File source:",
        # Uncomment this later when everything is finalised
        # options=["From API", "File Upload"],
        options=[
            "From API",
            "File Upload",
            "Load Local Data",
        ],  # Only for development - to be removed later
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
    elif source_type == "File Upload":
        uploaded_files = st.file_uploader(
            f"Upload {source} file(s):",
            accept_multiple_files=True,
            type=["json"],
            key="opwy_upload",
        )

        if st.button("Finish", key="finish_upload"):
            with st.spinner("Validating files..."):
                if source == "Opta":
                    st.markdown(
                        f"**Validating uploaded files** (Expecting: {', '.join(expected_opta_files)}):"
                    )
                    for file in uploaded_files:
                        # Check file type first
                        if file.type != "application/json":
                            st.markdown(
                                f"- ❌ {file.name} - Invalid file type (must be JSON)"
                            )
                            uploaded_files.remove(file)
                        # Check file name for expected Opta files
                        if not any(
                            expected_file in file.name.lower()
                            for expected_file in expected_opta_files
                        ):
                            st.markdown(f"- ❌ {file.name} - Unrecognised file!")
                            uploaded_files.remove(file)
                        else:
                            matched_file = next(
                                expected_file
                                for expected_file in expected_opta_files
                                if expected_file in file.name.lower()
                            )
                            st.markdown(f"- ✅ {file.name} - {matched_file} file found")

                # Store the uploaded files in the temp folder
                for file in uploaded_files:
                    with open(f"data/tmp/{file.name}", "wb") as f:
                        f.write(file.getbuffer())

                    uploaded_file_names.append("data/tmp/" + file.name)

    else:  # Load Local Data (for development only - to be removed later)
        st.warning("Loading local data from data/opta folder (for development only).")
        # List all files in the data/tmp/ folder
        import os

        local_files = os.listdir("data/opta/U23 Asian Cup")
        st.markdown(f"**Local files found:** {', '.join(local_files)}")
        for file in local_files:
            uploaded_file_names.append("data/opta/U23 Asian Cup/" + file)

    for file_name in uploaded_file_names:
        loaded_json = load_json(file_name)
        st.markdown(f"- ✅ Loaded {file_name}")

    return uploaded_file_names


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
