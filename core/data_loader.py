from __future__ import annotations

import os
from pathlib import Path
from typing import IO

import pandas as pd

from config.defaults import DEFAULT_REFERENCE_EXTENSIONS


def load_reference_from_file(file_obj, sheet_name=0) -> pd.DataFrame:
    """Load a reference database from an uploaded file object."""
    name = getattr(file_obj, "name", "") or ""
    if name.endswith(".csv"):
        return pd.read_csv(file_obj, dtype=str).fillna("")
    return pd.read_excel(file_obj, sheet_name=sheet_name, dtype=str).fillna("")


def load_reference_from_folder(
    folder_path: str,
    extensions: tuple = DEFAULT_REFERENCE_EXTENSIONS,
) -> pd.DataFrame:
    """Concatenate all matching files in a folder into one DataFrame."""
    files = list_folder_files(folder_path, extensions)
    if not files:
        raise FileNotFoundError(f"No files found in folder: {folder_path}")
    frames = []
    for f in files:
        if f.endswith(".csv"):
            frames.append(pd.read_csv(f, dtype=str).fillna(""))
        else:
            frames.append(pd.read_excel(f, dtype=str).fillna(""))
    return pd.concat(frames, ignore_index=True)


def load_query_sheet(file_obj, sheet_name=0) -> pd.DataFrame:
    """Load the query sheet from an uploaded file object."""
    name = getattr(file_obj, "name", "") or ""
    if name.endswith(".csv"):
        return pd.read_csv(file_obj, dtype=str).fillna("")
    return pd.read_excel(file_obj, sheet_name=sheet_name, dtype=str).fillna("")


def detect_id_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Return the first column whose normalized name appears in candidates."""
    norm = {c.lower().strip().replace(" ", "_"): c for c in df.columns}
    for cand in candidates:
        key = cand.lower().strip().replace(" ", "_")
        if key in norm:
            return norm[key]
    # Fallback: first column whose name contains "id"
    for col in df.columns:
        if "id" in col.lower():
            return col
    return None


def deduplicate_df(df: pd.DataFrame, key_col: str, keep: str = "first") -> tuple[pd.DataFrame, int]:
    """Return (deduped_df, n_removed). keep: 'first' | 'last'."""
    before = len(df)
    deduped = df.drop_duplicates(subset=[key_col], keep=keep).reset_index(drop=True)
    return deduped, before - len(deduped)


def detect_name_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Return the first column whose normalized name appears in candidates."""
    norm = {c.lower().strip().replace(" ", "_"): c for c in df.columns}
    for cand in candidates:
        key = cand.lower().strip().replace(" ", "_")
        if key in norm:
            return norm[key]
    return None


def list_folder_files(folder_path: str, extensions: tuple) -> list[str]:
    """Return absolute paths to files with matching extensions in folder_path."""
    p = Path(folder_path)
    if not p.is_dir():
        return []
    return sorted(
        str(f) for f in p.iterdir()
        if f.is_file() and f.suffix.lower() in extensions
    )


def get_sheet_names(file_obj) -> list[str]:
    """Return sheet names for an Excel file object; returns ['Sheet1'] for CSVs."""
    name = getattr(file_obj, "name", "") or ""
    if name.endswith(".csv"):
        return ["Sheet1"]
    try:
        xf = pd.ExcelFile(file_obj)
        return xf.sheet_names
    except Exception:
        return ["Sheet1"]
