from __future__ import annotations

import streamlit as st

from core.data_loader import (
    detect_id_column, detect_name_column,
    load_reference_from_file, load_reference_from_folder,
    load_query_sheet, list_folder_files, get_sheet_names,
)
from config.defaults import DEFAULT_ID_COLUMN_CANDIDATES, DEFAULT_NAME_COLUMN_CANDIDATES
from ui.components import callout, file_preview_card
from data.example_datasets import EXAMPLE_DATASETS, DATASET_NAMES, get_dataset


def render_page_load() -> None:
    st.header("Step 1 of 3 — Load Data")
    st.markdown("Upload your reference database and query sheet to get started.")

    _render_example_data_section()
    st.markdown("---")
    _render_reference_section()
    st.markdown("---")
    _render_query_section()
    _render_continue_button()


# ---------------------------------------------------------------------------
# Example data section
# ---------------------------------------------------------------------------

def _render_example_data_section() -> None:
    with st.expander("Try with example data", expanded=False):
        st.markdown(
            "Load one of the built-in challenging datasets to explore how the matcher handles "
            "real-world ID formatting problems."
        )

        selected = st.selectbox(
            "Choose a dataset",
            DATASET_NAMES,
            key="example_dataset_select",
        )
        dataset = get_dataset(selected)

        if dataset:
            st.markdown(f"**About this dataset:** {dataset['description']}")
            st.markdown("**Challenges included:**")
            for c in dataset["challenges"]:
                st.markdown(f"- {c}")

            col_ref, col_query = st.columns(2)
            with col_ref:
                st.caption(f"Reference: {len(dataset['ref_df'])} rows")
                st.dataframe(dataset["ref_df"].head(4), use_container_width=True, hide_index=True)
            with col_query:
                st.caption(f"Query: {len(dataset['query_df'])} rows")
                st.dataframe(dataset["query_df"].head(4), use_container_width=True, hide_index=True)

            if st.button("Load this example dataset", type="primary", key="load_example_btn"):
                st.session_state["ref_df"]       = dataset["ref_df"].copy()
                st.session_state["ref_filename"]  = f"[Example] {dataset['name']} — Reference"
                st.session_state["query_df"]      = dataset["query_df"].copy()
                st.session_state["query_filename"] = f"[Example] {dataset['name']} — Query"
                st.session_state["ref_id_col"]    = dataset["ref_id_col"]
                st.session_state["ref_name_col"]  = dataset["ref_name_col"]
                st.session_state["query_id_col"]  = dataset["query_id_col"]
                st.rerun()


# ---------------------------------------------------------------------------
# Reference section
# ---------------------------------------------------------------------------

def _render_reference_section() -> None:
    st.subheader("Reference Database")

    load_mode = st.radio(
        "How would you like to load the reference?",
        ["Upload a single file", "Specify a folder path"],
        horizontal=True,
        key="ref_load_mode",
    )

    if load_mode == "Upload a single file":
        _handle_reference_file_upload()
    else:
        _handle_reference_folder()


def _handle_reference_file_upload() -> None:
    uploaded = st.file_uploader(
        "Reference database file",
        type=["xlsx", "xls", "csv"],
        key="ref_file_upload",
        label_visibility="collapsed",
        help="Upload the master reference file (.xlsx, .xls, or .csv)",
    )

    if uploaded is not None:
        # Sheet selection for Excel files
        sheet = 0
        if not uploaded.name.endswith(".csv"):
            sheet_names = get_sheet_names(uploaded)
            if len(sheet_names) > 1:
                sheet = st.selectbox(
                    "Select sheet",
                    sheet_names,
                    key="ref_sheet_select",
                )
                sheet = sheet_names.index(sheet)
            uploaded.seek(0)

        try:
            df = load_reference_from_file(uploaded, sheet_name=sheet)
            st.session_state["ref_df"] = df
            st.session_state["ref_filename"] = uploaded.name
            _auto_detect_columns(df, "ref")
            file_preview_card(uploaded.name, len(df), list(df.columns), df)
        except Exception as e:
            callout(f"Failed to load reference file: {e}", kind="error")
    elif st.session_state.get("ref_df") is not None:
        ref_df = st.session_state["ref_df"]
        file_preview_card(
            st.session_state.get("ref_filename", "reference"),
            len(ref_df),
            list(ref_df.columns),
            ref_df,
        )
        if st.button("× Remove reference", key="remove_ref"):
            st.session_state.pop("ref_df", None)
            st.session_state.pop("ref_filename", None)
            st.rerun()


def _handle_reference_folder() -> None:
    folder = st.text_input(
        "Folder path containing reference files",
        key="ref_folder_input",
        placeholder="/path/to/reference/folder",
    )
    if st.button("Load from folder", key="load_folder_btn"):
        if not folder:
            callout("Please enter a folder path.", kind="warning")
            return
        try:
            df = load_reference_from_folder(folder)
            st.session_state["ref_df"] = df
            st.session_state["ref_filename"] = f"Folder: {folder}"
            _auto_detect_columns(df, "ref")
            file_preview_card(f"Folder: {folder}", len(df), list(df.columns), df)
        except Exception as e:
            callout(f"Failed to load folder: {e}", kind="error")
    elif st.session_state.get("ref_df") is not None:
        ref_df = st.session_state["ref_df"]
        file_preview_card(
            st.session_state.get("ref_filename", "reference"),
            len(ref_df),
            list(ref_df.columns),
            ref_df,
        )


# ---------------------------------------------------------------------------
# Query section
# ---------------------------------------------------------------------------

def _render_query_section() -> None:
    st.subheader("Query Sheet")

    uploaded = st.file_uploader(
        "Query sheet file",
        type=["xlsx", "xls", "csv"],
        key="query_file_upload",
        label_visibility="collapsed",
        help="Upload the sheet containing the sample IDs you want to look up",
    )

    if uploaded is not None:
        sheet = 0
        if not uploaded.name.endswith(".csv"):
            sheet_names = get_sheet_names(uploaded)
            if len(sheet_names) > 1:
                sheet = st.selectbox(
                    "Select sheet (query)",
                    sheet_names,
                    key="query_sheet_select",
                )
                sheet = sheet_names.index(sheet)
            uploaded.seek(0)

        try:
            df = load_query_sheet(uploaded, sheet_name=sheet)
            st.session_state["query_df"] = df
            st.session_state["query_filename"] = uploaded.name
            _auto_detect_columns(df, "query")
            file_preview_card(uploaded.name, len(df), list(df.columns), df)
        except Exception as e:
            callout(f"Failed to load query file: {e}", kind="error")
    elif st.session_state.get("query_df") is not None:
        q_df = st.session_state["query_df"]
        file_preview_card(
            st.session_state.get("query_filename", "query"),
            len(q_df),
            list(q_df.columns),
            q_df,
        )
        if st.button("× Remove query", key="remove_query"):
            st.session_state.pop("query_df", None)
            st.session_state.pop("query_filename", None)
            st.rerun()


# ---------------------------------------------------------------------------
# Continue button
# ---------------------------------------------------------------------------

def _render_continue_button() -> None:
    ref_ready   = st.session_state.get("ref_df") is not None
    query_ready = st.session_state.get("query_df") is not None

    st.markdown("")
    if ref_ready and query_ready:
        if st.button("Continue to Configure →", type="primary", key="continue_to_config"):
            st.session_state["current_step"] = 2
            st.rerun()
    else:
        missing = []
        if not ref_ready:
            missing.append("reference database")
        if not query_ready:
            missing.append("query sheet")
        st.info(f"Please load your {' and '.join(missing)} to continue.")


# ---------------------------------------------------------------------------
# Auto-detection helper
# ---------------------------------------------------------------------------

def _auto_detect_columns(df, prefix: str) -> None:
    """Detect ID and name columns and store to session state."""
    id_col   = detect_id_column(df, DEFAULT_ID_COLUMN_CANDIDATES)
    name_col = detect_name_column(df, DEFAULT_NAME_COLUMN_CANDIDATES)
    if prefix == "ref":
        if id_col:
            st.session_state["ref_id_col"] = id_col
        if name_col:
            st.session_state["ref_name_col"] = name_col
    elif prefix == "query":
        if id_col:
            st.session_state["query_id_col"] = id_col
