"""
Shared matching execution logic — called from both page_configure and the
sidebar re-run panel so both stay in sync.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from core.matcher import MatchConfig, MatchResult, match_all
from core.report_generator import build_results_df, build_unmatched_df, compute_summary_stats
from core.data_loader import deduplicate_df


def run_matching(
    ref_df: pd.DataFrame,
    query_df: pd.DataFrame,
    ref_id_col: str,
    ref_name_col: str | None,
    query_id_col: str,
    config: MatchConfig,
    manual_mappings: dict[str, MatchResult] | None = None,
    advance_to_step3: bool = True,
    dedup_ref: bool = False,
    dedup_query: bool = False,
    dedup_keep: str = "first",
    dedup_ref_key: str | None = None,
    dedup_query_key: str | None = None,
) -> None:
    """
    Execute matching, apply manual overrides, persist results to session state,
    and (optionally) advance to Step 3.
    """
    manual_mappings = manual_mappings or {}

    ref_removed = query_removed = 0
    if dedup_ref:
        ref_df, ref_removed = deduplicate_df(ref_df, dedup_ref_key or ref_id_col, keep=dedup_keep)
    if dedup_query:
        query_df, query_removed = deduplicate_df(query_df, dedup_query_key or query_id_col, keep=dedup_keep)

    with st.spinner("Running matching…"):
        try:
            results = match_all(
                query_df[query_id_col].astype(str).tolist(),
                ref_df,
                config,
                ref_id_col=ref_id_col,
                ref_name_col=ref_name_col,
            )
        except Exception as e:
            st.error(f"Matching failed: {e}")
            return

    # Apply manual overrides
    final_results = [
        manual_mappings.get(r.query_id, r) for r in results
    ]

    results_df   = build_results_df(final_results, ref_df, ref_id_col)
    unmatched_df = build_unmatched_df(final_results)
    matched_df   = results_df[results_df["Matched"] == True].drop(
        columns=["Matched", "Reason"], errors="ignore"
    )
    summary = compute_summary_stats(final_results)
    summary["ref_dupes_removed"]   = ref_removed
    summary["query_dupes_removed"] = query_removed

    st.session_state["ref_id_col"]    = ref_id_col
    st.session_state["ref_name_col"]  = ref_name_col
    st.session_state["query_id_col"]  = query_id_col
    st.session_state["match_config"]  = config
    st.session_state["results_df"]    = results_df
    st.session_state["matched_df"]    = matched_df
    st.session_state["unmatched_df"]  = unmatched_df
    st.session_state["summary_stats"] = summary

    if advance_to_step3:
        st.session_state["current_step"] = 3

    st.rerun()
