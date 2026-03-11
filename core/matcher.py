from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

import pandas as pd
from rapidfuzz import fuzz, process

from config.defaults import DEFAULT_FUZZY_THRESHOLD, UNMATCHED_REASONS


@dataclass
class MatchConfig:
    use_exact: bool = True
    use_substring: bool = True
    use_fuzzy: bool = True
    fuzzy_threshold: int = DEFAULT_FUZZY_THRESHOLD
    strip_special: bool = True
    normalize_padding: bool = False


@dataclass
class MatchResult:
    query_id: str
    matched_ref_id: str | None
    sample_name: str | None
    strategy: str        # "exact" | "exact_norm" | "substring" | "fuzzy" | "no_match"
    score: float         # 100.0 for exact, 0.0 for no_match
    reason: str | None   # Human-readable explanation for unmatched only
    best_candidate: str | None = None  # Closest ref ID even if below threshold


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

def _to_ascii(s: str) -> str:
    """Replace accented characters with ASCII equivalents."""
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


def normalize(s: str, aggressive: bool = False) -> str:
    """
    Basic: lowercase + strip whitespace.
    Aggressive: also strip -, _, and runs of whitespace, convert to ASCII.
    """
    s = _to_ascii(str(s)).strip().lower()
    if aggressive:
        s = re.sub(r"[\-_\s]+", "", s)
    return s


def _normalize_padding(s: str) -> str:
    """Normalize numeric padding: S-1 and S-01 both become S-1."""
    return re.sub(r"0*(\d+)", r"\1", s)


# ---------------------------------------------------------------------------
# Core matching
# ---------------------------------------------------------------------------

def match_single(
    query_id: str,
    reference_ids: list[str],
    config: MatchConfig,
    ref_name_map: dict[str, str] | None = None,
) -> MatchResult:
    """Match a single query ID against a list of reference IDs."""
    ref_name_map = ref_name_map or {}

    def make_result(ref_id, strategy, score, reason=None, best_candidate=None):
        name = ref_name_map.get(ref_id) if ref_id else None
        return MatchResult(
            query_id=query_id,
            matched_ref_id=ref_id,
            sample_name=name,
            strategy=strategy,
            score=score,
            reason=reason,
            best_candidate=best_candidate,
        )

    # Guard: empty / null ID
    raw = str(query_id).strip()
    if not raw or raw.lower() in ("nan", "none", ""):
        return make_result(None, "no_match", 0.0, UNMATCHED_REASONS["empty_id"])

    if not reference_ids:
        return make_result(None, "no_match", 0.0, UNMATCHED_REASONS["no_candidates"])

    # --- 1. Exact match (case + whitespace normalised) -----------------------
    if config.use_exact:
        q_basic = normalize(raw, aggressive=False)
        for ref in reference_ids:
            if normalize(ref, aggressive=False) == q_basic:
                return make_result(ref, "exact", 100.0)

    # --- 2. Exact aggressive (strip special chars) ---------------------------
    if config.use_exact and config.strip_special:
        q_agg = normalize(raw, aggressive=True)
        for ref in reference_ids:
            if normalize(ref, aggressive=True) == q_agg:
                return make_result(ref, "exact_norm", 100.0)

    # --- 3. Numeric-padding normalization ------------------------------------
    if config.use_exact and config.normalize_padding:
        q_pad = _normalize_padding(normalize(raw, aggressive=True))
        for ref in reference_ids:
            if _normalize_padding(normalize(ref, aggressive=True)) == q_pad:
                return make_result(ref, "exact_norm", 100.0)

    # --- 4. Substring match --------------------------------------------------
    if config.use_substring:
        q_low = normalize(raw, aggressive=False)
        if len(q_low) >= 3:
            for ref in reference_ids:
                r_low = normalize(ref, aggressive=False)
                if q_low in r_low or r_low in q_low:
                    return make_result(ref, "substring", 100.0)

    # --- 5. Fuzzy match (token_set_ratio → handles word-order & substrings) --
    if config.use_fuzzy:
        hit = process.extractOne(
            raw,
            reference_ids,
            scorer=fuzz.token_set_ratio,
            score_cutoff=0,
        )
        if hit is not None:
            best_ref, best_score, _ = hit
            if best_score >= config.fuzzy_threshold:
                return make_result(best_ref, "fuzzy", float(best_score))
            else:
                return make_result(
                    None, "no_match", 0.0,
                    UNMATCHED_REASONS["below_threshold"],
                    best_candidate=best_ref,
                )

    return make_result(None, "no_match", 0.0, UNMATCHED_REASONS["no_candidates"])


def match_all(
    query_ids: list[str],
    reference_df: pd.DataFrame,
    config: MatchConfig,
    ref_id_col: str = None,
    ref_name_col: str = None,
) -> list[MatchResult]:
    """Match all query IDs against the reference DataFrame."""
    if ref_id_col is None or ref_id_col not in reference_df.columns:
        raise ValueError(f"Reference ID column '{ref_id_col}' not found in reference DataFrame.")

    ref_ids = reference_df[ref_id_col].astype(str).tolist()
    # De-duplicate while preserving first occurrence
    seen: dict[str, int] = {}
    unique_refs: list[str] = []
    for r in ref_ids:
        if r not in seen:
            seen[r] = len(unique_refs)
            unique_refs.append(r)

    ref_name_map: dict[str, str] = {}
    if ref_name_col and ref_name_col in reference_df.columns:
        for _, row in reference_df[[ref_id_col, ref_name_col]].drop_duplicates(
            subset=ref_id_col, keep="first"
        ).iterrows():
            ref_name_map[str(row[ref_id_col])] = str(row[ref_name_col])

    results = []
    for qid in query_ids:
        results.append(match_single(qid, unique_refs, config, ref_name_map))
    return results
