"""Unit tests for core/report_generator.py."""
from __future__ import annotations

import pandas as pd
import pytest

from core.matcher import MatchConfig, MatchResult, match_all
from core.report_generator import (
    build_results_df,
    build_unmatched_df,
    compute_summary_stats,
)
from config.defaults import STRATEGY_LABELS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_results():
    return [
        MatchResult("S001", "SAMPLE_001", "Alpha", "exact",     100.0, None),
        MatchResult("S002", "SAMPLE_002", "Beta",  "fuzzy",      85.0, None),
        MatchResult("S003", None,         None,    "no_match",    0.0, "No similar IDs found"),
        MatchResult("S004", "SAMPLE_003", "Gamma", "substring", 100.0, None),
    ]


# ---------------------------------------------------------------------------
# compute_summary_stats
# ---------------------------------------------------------------------------

def test_summary_total():
    stats = compute_summary_stats(_make_results())
    assert stats["total"] == 4


def test_summary_matched():
    stats = compute_summary_stats(_make_results())
    assert stats["matched"] == 3


def test_summary_unmatched():
    stats = compute_summary_stats(_make_results())
    assert stats["unmatched"] == 1


def test_summary_match_rate():
    stats = compute_summary_stats(_make_results())
    assert stats["match_rate"] == 75.0


def test_summary_by_strategy():
    stats = compute_summary_stats(_make_results())
    bys = stats["by_strategy"]
    assert bys[STRATEGY_LABELS["exact"]] == 1
    assert bys[STRATEGY_LABELS["fuzzy"]] == 1
    assert bys[STRATEGY_LABELS["substring"]] == 1


def test_summary_empty():
    stats = compute_summary_stats([])
    assert stats["total"] == 0
    assert stats["matched"] == 0
    assert stats["match_rate"] == 0.0


# ---------------------------------------------------------------------------
# build_results_df
# ---------------------------------------------------------------------------

def test_results_df_shape():
    df = build_results_df(_make_results(), ref_df=None)
    assert len(df) == 4
    assert "Query ID" in df.columns
    assert "Matched ID" in df.columns
    assert "Strategy" in df.columns


def test_results_df_matched_flag():
    df = build_results_df(_make_results(), ref_df=None)
    matched = df[df["Matched"] == True]
    assert len(matched) == 3


def test_results_df_score_numeric():
    df = build_results_df(_make_results(), ref_df=None)
    fuzzy_row = df[df["Query ID"] == "S002"].iloc[0]
    assert fuzzy_row["Score"] == 85.0


def test_results_df_score_blank_for_exact():
    df = build_results_df(_make_results(), ref_df=None)
    exact_row = df[df["Query ID"] == "S001"].iloc[0]
    assert exact_row["Score"] == ""


# ---------------------------------------------------------------------------
# build_unmatched_df
# ---------------------------------------------------------------------------

def test_unmatched_df_only_unmatched():
    df = build_unmatched_df(_make_results())
    assert len(df) == 1
    assert df.iloc[0]["Query ID"] == "S003"


def test_unmatched_df_reason():
    df = build_unmatched_df(_make_results())
    assert "No similar" in df.iloc[0]["Reason"]


def test_unmatched_df_empty_when_all_matched():
    results = [
        MatchResult("S001", "SAMPLE_001", "A", "exact", 100.0, None),
    ]
    df = build_unmatched_df(results)
    assert df.empty


# ---------------------------------------------------------------------------
# Integration with match_all
# ---------------------------------------------------------------------------

def test_full_pipeline_report(reference_df):
    cfg = MatchConfig(fuzzy_threshold=70)
    query_ids = ["SAMPLE_001", "sample_002", "SAMPL_003", "ZZZ_NONE"]
    results = match_all(query_ids, reference_df, cfg, ref_id_col="SampleID", ref_name_col="Name")
    stats = compute_summary_stats(results)
    assert stats["total"] == 4
    assert stats["matched"] >= 3  # at least exact + fuzzy matches

    results_df = build_results_df(results, reference_df, ref_id_col="SampleID")
    assert len(results_df) == 4
