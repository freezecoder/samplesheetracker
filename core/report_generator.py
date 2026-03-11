from __future__ import annotations

from collections import Counter

import pandas as pd

from core.matcher import MatchResult
from config.defaults import STRATEGY_LABELS


def build_results_df(
    match_results: list[MatchResult],
    ref_df: pd.DataFrame,
    ref_id_col: str = None,
) -> pd.DataFrame:
    """Build a DataFrame from all match results, joined with any extra ref columns."""
    rows = []
    for r in match_results:
        rows.append({
            "Query ID":    r.query_id,
            "Matched ID":  r.matched_ref_id or "",
            "Sample Name": r.sample_name or "",
            "Strategy":    STRATEGY_LABELS.get(r.strategy, r.strategy),
            "Score":       r.score if r.strategy not in ("exact", "exact_norm", "substring") else "",
            "Matched":     r.strategy != "no_match",
            "Reason":      r.reason or "",
        })
    df = pd.DataFrame(rows)

    # Join additional reference columns (excluding id + name already present)
    if ref_df is not None and ref_id_col and ref_id_col in ref_df.columns:
        extra_cols = [c for c in ref_df.columns if c != ref_id_col]
        ref_slim = ref_df[[ref_id_col] + extra_cols].drop_duplicates(
            subset=ref_id_col, keep="first"
        ).rename(columns={ref_id_col: "Matched ID"})
        df = df.merge(ref_slim, on="Matched ID", how="left")

    return df


def build_unmatched_df(match_results: list[MatchResult]) -> pd.DataFrame:
    rows = [
        {
            "Query ID":        r.query_id,
            "Reason":          r.reason or "",
            "Best Candidate":  r.best_candidate or "",
        }
        for r in match_results
        if r.strategy == "no_match"
    ]
    return pd.DataFrame(rows)


def compute_summary_stats(match_results: list[MatchResult]) -> dict:
    """Return summary statistics as a plain dict."""
    total = len(match_results)
    matched = sum(1 for r in match_results if r.strategy != "no_match")
    unmatched = total - matched
    rate = (matched / total * 100) if total > 0 else 0.0

    strategy_counts = Counter(
        STRATEGY_LABELS.get(r.strategy, r.strategy)
        for r in match_results
        if r.strategy != "no_match"
    )

    return {
        "total":           total,
        "matched":         matched,
        "unmatched":       unmatched,
        "match_rate":      round(rate, 1),
        "by_strategy":     dict(strategy_counts),
    }
