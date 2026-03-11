"""Shared fixtures for Sample Sheet Tracker tests."""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Reference DataFrame fixture
# ---------------------------------------------------------------------------

REFERENCE_ROWS = [
    {"SampleID": "SAMPLE_001", "Name": "Alpha-01", "Batch": "B01"},
    {"SampleID": "SAMPLE_002", "Name": "Alpha-02", "Batch": "B01"},
    {"SampleID": "SAMPLE_003", "Name": "Beta-01",  "Batch": "B02"},
    {"SampleID": "SAMPLE_01",  "Name": "Short-01", "Batch": "B03"},
    {"SampleID": "LAB_S001_A", "Name": "Lab-S001", "Batch": "B04"},
    {"SampleID": "S001",       "Name": "Short-S001","Batch": "B04"},
    {"SampleID": "AB_LONG",    "Name": "AB-long",  "Batch": "B05"},
    {"SampleID": "ABCD",       "Name": "AB-cd",    "Batch": "B05"},
    {"SampleID": "12345",      "Name": "Numeric",  "Batch": "B06"},
    {"SampleID": "John Smith", "Name": "Person-01","Batch": "B07"},
    {"SampleID": "Sample_001", "Name": "Unicode-ref","Batch": "B08"},
]


@pytest.fixture
def reference_df() -> pd.DataFrame:
    return pd.DataFrame(REFERENCE_ROWS)


@pytest.fixture
def small_query_df() -> pd.DataFrame:
    return pd.DataFrame({
        "QueryID": [
            "SAMPLE_001",   # exact
            "sample_001",   # exact (case)
            "SAMPLE 001",   # exact_norm (space)
            "SAMPLE-001",   # exact_norm (dash)
            "S001",         # substring
            "LAB_S001_A",   # substring (ref ⊂ query direction)
            "SAMPL_001",    # fuzzy (typo)
            "SMAPLE_001",   # fuzzy (transposed)
            "XYZ999_UNKNOWN",  # no_match
            "",             # empty
            "12345",        # exact numeric
            "Smith John",   # fuzzy (word order)
        ]
    })


# ---------------------------------------------------------------------------
# File fixtures (generate programmatic Excel/CSV files)
# ---------------------------------------------------------------------------

@pytest.fixture
def reference_xlsx_path(tmp_path: Path, reference_df: pd.DataFrame) -> Path:
    p = tmp_path / "reference_db.xlsx"
    reference_df.to_excel(p, index=False)
    return p


@pytest.fixture
def query_xlsx_path(tmp_path: Path, small_query_df: pd.DataFrame) -> Path:
    p = tmp_path / "query_sheet.xlsx"
    small_query_df.to_excel(p, index=False)
    return p


@pytest.fixture
def reference_csv_path(tmp_path: Path, reference_df: pd.DataFrame) -> Path:
    p = tmp_path / "reference_db.csv"
    reference_df.to_csv(p, index=False)
    return p


@pytest.fixture
def multi_sheet_ref_path(tmp_path: Path, reference_df: pd.DataFrame) -> Path:
    p = tmp_path / "multi_sheet_ref.xlsx"
    with pd.ExcelWriter(p, engine="openpyxl") as w:
        reference_df.iloc[:5].to_excel(w, sheet_name="Batch1", index=False)
        reference_df.iloc[5:].to_excel(w, sheet_name="Batch2", index=False)
    return p


@pytest.fixture
def reference_folder(tmp_path: Path, reference_df: pd.DataFrame) -> Path:
    folder = tmp_path / "ref_folder"
    folder.mkdir()
    reference_df.iloc[:6].to_excel(folder / "part1.xlsx", index=False)
    reference_df.iloc[6:].to_csv(folder / "part2.csv", index=False)
    return folder
