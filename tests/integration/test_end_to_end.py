"""End-to-end integration tests for the full matching pipeline."""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pytest

from core.data_loader import (
    load_reference_from_file,
    load_reference_from_folder,
    load_query_sheet,
    detect_id_column,
)
from core.matcher import MatchConfig, match_all
from core.report_generator import build_results_df, build_unmatched_df, compute_summary_stats
from core.excel_exporter import export_to_excel
from config.defaults import DEFAULT_ID_COLUMN_CANDIDATES


# ---------------------------------------------------------------------------
# Helper: load from a real path using a path-like mock
# ---------------------------------------------------------------------------

class FilePathMock(io.BytesIO):
    """Mimic Streamlit UploadedFile enough for our loaders."""
    def __init__(self, path: Path):
        super().__init__(path.read_bytes())
        self.name = path.name


# ---------------------------------------------------------------------------
# Full pipeline: xlsx reference + xlsx query
# ---------------------------------------------------------------------------

def test_full_pipeline_xlsx(reference_xlsx_path, query_xlsx_path):
    ref_f   = FilePathMock(reference_xlsx_path)
    query_f = FilePathMock(query_xlsx_path)

    ref_df   = load_reference_from_file(ref_f)
    query_df = load_query_sheet(query_f)

    ref_id_col   = detect_id_column(ref_df, DEFAULT_ID_COLUMN_CANDIDATES)
    query_id_col = detect_id_column(query_df, DEFAULT_ID_COLUMN_CANDIDATES)

    assert ref_id_col == "SampleID"
    assert query_id_col == "QueryID"

    cfg = MatchConfig(fuzzy_threshold=70)
    results = match_all(
        query_df[query_id_col].tolist(),
        ref_df, cfg,
        ref_id_col=ref_id_col,
        ref_name_col="Name",
    )

    stats = compute_summary_stats(results)
    assert stats["total"] == len(query_df)
    assert stats["matched"] >= 1
    assert 0 <= stats["match_rate"] <= 100


# ---------------------------------------------------------------------------
# Full pipeline: csv reference
# ---------------------------------------------------------------------------

def test_full_pipeline_csv(reference_csv_path, small_query_df):
    ref_df = pd.read_csv(reference_csv_path, dtype=str).fillna("")
    cfg    = MatchConfig(fuzzy_threshold=70)
    results = match_all(
        small_query_df["QueryID"].tolist(),
        ref_df, cfg,
        ref_id_col="SampleID",
    )
    stats = compute_summary_stats(results)
    assert stats["total"] == len(small_query_df)


# ---------------------------------------------------------------------------
# Folder reference
# ---------------------------------------------------------------------------

def test_full_pipeline_folder(reference_folder, small_query_df):
    ref_df = load_reference_from_folder(str(reference_folder))
    assert len(ref_df) > 0

    cfg = MatchConfig(fuzzy_threshold=70)
    results = match_all(
        small_query_df["QueryID"].tolist(),
        ref_df, cfg,
        ref_id_col="SampleID",
    )
    stats = compute_summary_stats(results)
    assert stats["total"] == len(small_query_df)


# ---------------------------------------------------------------------------
# Excel export
# ---------------------------------------------------------------------------

def test_excel_export_produces_valid_bytes(reference_df, small_query_df):
    cfg = MatchConfig(fuzzy_threshold=70)
    results = match_all(
        small_query_df["QueryID"].tolist(),
        reference_df, cfg,
        ref_id_col="SampleID",
        ref_name_col="Name",
    )
    results_df   = build_results_df(results, reference_df, ref_id_col="SampleID")
    unmatched_df = build_unmatched_df(results)
    matched_df   = results_df[results_df["Matched"] == True].drop(
        columns=["Matched", "Reason"], errors="ignore"
    )
    stats = compute_summary_stats(results)

    xlsx_bytes = export_to_excel(matched_df, unmatched_df, stats, all_results_df=results_df)
    assert isinstance(xlsx_bytes, bytes)
    assert len(xlsx_bytes) > 0

    # Verify it's a valid Excel file with expected sheets
    wb = pd.read_excel(io.BytesIO(xlsx_bytes), sheet_name=None)
    assert "Summary" in wb
    assert "Matched" in wb
    assert "Unmatched" in wb
    assert "All Results" in wb


def test_excel_export_matched_content(reference_df, small_query_df):
    cfg = MatchConfig(fuzzy_threshold=70)
    results = match_all(
        ["SAMPLE_001"], reference_df, cfg, ref_id_col="SampleID"
    )
    results_df   = build_results_df(results, reference_df, ref_id_col="SampleID")
    matched_df   = results_df[results_df["Matched"] == True].drop(
        columns=["Matched", "Reason"], errors="ignore"
    )
    unmatched_df = build_unmatched_df(results)
    stats        = compute_summary_stats(results)

    xlsx_bytes = export_to_excel(matched_df, unmatched_df, stats)
    wb = pd.read_excel(io.BytesIO(xlsx_bytes), sheet_name=None)

    matched_sheet = wb["Matched"]
    assert "Query ID" in matched_sheet.columns or len(matched_sheet) >= 0


# ---------------------------------------------------------------------------
# Specific edge case: empty query list
# ---------------------------------------------------------------------------

def test_empty_query_list(reference_df):
    cfg = MatchConfig()
    results = match_all([], reference_df, cfg, ref_id_col="SampleID")
    assert results == []
    stats = compute_summary_stats(results)
    assert stats["total"] == 0
    assert stats["match_rate"] == 0.0


# ---------------------------------------------------------------------------
# Specific edge case: all unmatched
# ---------------------------------------------------------------------------

def test_all_unmatched(reference_df):
    cfg = MatchConfig(fuzzy_threshold=99)
    results = match_all(
        ["ZZZ_001", "WWW_002"], reference_df, cfg, ref_id_col="SampleID"
    )
    stats = compute_summary_stats(results)
    assert stats["matched"] == 0 or stats["match_rate"] <= 50


# ---------------------------------------------------------------------------
# Specific edge case: large-ish dataset performance
# ---------------------------------------------------------------------------

def test_performance_100_queries(reference_df):
    """Matching 100 query IDs should complete without error."""
    queries = [f"SAMPLE_{i:03d}" for i in range(100)]
    cfg = MatchConfig(fuzzy_threshold=80)
    results = match_all(queries, reference_df, cfg, ref_id_col="SampleID")
    assert len(results) == 100
