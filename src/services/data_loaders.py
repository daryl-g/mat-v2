# Data loading functions for different data sources

# Imports
import os

import streamlit as st

from utils import load_json
from .scrapers import Scrapers


_VALID_OPTA_SUFFIXES = ("stats.json", "events.json", "xgoal.json", "passmap.json")

_EXPECTED_OPTA_FILES = ["xgoal", "events", "passmap", "stats", "squad"]


def _validate_opta_files(uploaded_files: list) -> list:
    """
    Validate uploaded Opta files against expected names, emitting st.markdown
    feedback for each file.  Returns only the files that passed validation.
    """
    st.markdown(
        f"**Validating uploaded files** (Expecting: {', '.join(_EXPECTED_OPTA_FILES)}):"
    )
    valid = []
    for file in uploaded_files:
        if file.type != "application/json":
            st.markdown(f"- \u274c {file.name} - Invalid file type (must be JSON)")
            continue
        matched = next(
            (e for e in _EXPECTED_OPTA_FILES if e in file.name.lower()), None
        )
        if matched is None:
            st.markdown(f"- \u274c {file.name} - Unrecognised file!")
        else:
            st.markdown(f"- \u2705 {file.name} - {matched} file found")
            valid.append(file)
    return valid


def _save_tmp_files(files: list) -> list[str]:
    """Write each file buffer to data/tmp/ and return the list of saved paths."""
    paths = []
    for file in files:
        path = f"data/tmp/{file.name}"
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        paths.append(path)
    return paths


def load_tmp_files() -> list:
    """
    Return paths of valid Opta match files already present in data/tmp/.
    Excludes temp.json and any file whose name does not match a known suffix.

    Returns:
        list: Sorted list of file paths, or an empty list if none found.
    """
    try:
        return sorted(
            f"data/tmp/{f}"
            for f in os.listdir("data/tmp")
            if f != "temp.json" and any(f.endswith(s) for s in _VALID_OPTA_SUFFIXES)
        )
    except FileNotFoundError:
        return []


def render_opta_wyscout_inputs(source: str) -> list:
    """
    Render input widgets for Opta/Wyscout data sources.

    Args:
        source (str): The data source name ("Opta" or "Wyscout").

    Returns:
        list: Uploaded files (if file upload selected), or empty list.
    """
    uploaded_file_names = []

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
            placeholder="e.g. 1a2b3c4d5e6f7g",
            key="match_id",
        )
        if st.button("Fetch", key="fetch_api"):
            result = Scrapers().opta_scraper(match_id)
            if result:
                uploaded_file_names = list(result.values())
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
                    uploaded_files = _validate_opta_files(uploaded_files)
                uploaded_file_names = _save_tmp_files(uploaded_files)

    else:  # Load Local Data (for development only - to be removed later)
        st.warning("Loading local data from data/opta folder (for development only).")
        # List all files in the data/tmp/ folder
        local_files = os.listdir("data/opta/U23 Asian Cup")
        st.markdown(f"**Local files found:** {', '.join(local_files)}")
        for file in local_files:
            uploaded_file_names.append("data/opta/U23 Asian Cup/" + file)

    # Persist successful file paths in session state so they survive reruns,
    # then immediately rerun so the loading block at the top of match.py
    # picks up the new files in the same interaction.
    if uploaded_file_names:
        st.session_state["uploaded_files"] = uploaded_file_names
        st.rerun()

    return st.session_state.get("uploaded_files", [])


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

    if source_type != "Open Data":
        # File Upload
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
            render_opta_wyscout_inputs(source)
        elif source in ["StatsBomb", "SkillCorner"]:
            render_statsbomb_skillcorner_inputs(source)

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
