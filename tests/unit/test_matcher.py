"""Unit tests for core/matcher.py — covers all 18 edge cases."""
from __future__ import annotations

import pytest

from core.matcher import MatchConfig, MatchResult, match_single, match_all, normalize


# Default permissive config used for most tests
DEFAULT_CFG = MatchConfig(
    use_exact=True,
    use_substring=True,
    use_fuzzy=True,
    fuzzy_threshold=70,
    strip_special=True,
    normalize_padding=False,
)

REFERENCES = [
    "SAMPLE_001", "SAMPLE_002", "SAMPLE_003",
    "SAMPLE_01",
    "LAB_S001_A", "S001",
    "AB_LONG", "ABCD",
    "12345",
    "John Smith",
    "Sample_001",
]


def _match(query_id: str, refs=None, cfg=None) -> MatchResult:
    return match_single(query_id, refs or REFERENCES, cfg or DEFAULT_CFG)


# ---------------------------------------------------------------------------
# Normalization helper
# ---------------------------------------------------------------------------

def test_normalize_basic():
    assert normalize("  HELLO  ") == "hello"


def test_normalize_aggressive():
    assert normalize("SAMPLE-001", aggressive=True) == "sample001"
    assert normalize("SAMPLE_001", aggressive=True) == "sample001"
    assert normalize("SAMPLE 001", aggressive=True) == "sample001"


# ---------------------------------------------------------------------------
# Edge case 1: Case difference
# ---------------------------------------------------------------------------

def test_case_difference():
    result = _match("sample_001")
    assert result.strategy == "exact"
    assert result.matched_ref_id == "SAMPLE_001"


# ---------------------------------------------------------------------------
# Edge case 2: Leading/trailing spaces
# ---------------------------------------------------------------------------

def test_leading_trailing_spaces():
    result = _match("  SAMPLE_001  ")
    assert result.strategy == "exact"
    assert result.matched_ref_id == "SAMPLE_001"


# ---------------------------------------------------------------------------
# Edge case 3: Internal spaces vs underscores
# ---------------------------------------------------------------------------

def test_internal_spaces_vs_underscores():
    result = _match("SAMPLE 001")
    assert result.strategy in ("exact_norm", "fuzzy")
    assert result.matched_ref_id == "SAMPLE_001"


# ---------------------------------------------------------------------------
# Edge case 4: Dashes vs underscores
# ---------------------------------------------------------------------------

def test_dashes_vs_underscores():
    result = _match("SAMPLE-001")
    assert result.strategy in ("exact_norm", "fuzzy")
    assert result.matched_ref_id == "SAMPLE_001"


# ---------------------------------------------------------------------------
# Edge case 5: Query is substring of reference
# ---------------------------------------------------------------------------

def test_query_substring_of_reference():
    result = _match("S001")
    # S001 is in REFERENCES directly, so exact match first
    assert result.strategy == "exact"
    assert result.matched_ref_id == "S001"


def test_query_substring_of_reference_not_exact():
    """Use a reference set where the query only appears as a substring."""
    refs = ["LAB_S001_A", "LAB_S002_B"]
    result = match_single("S001", refs, DEFAULT_CFG)
    assert result.strategy == "substring"
    assert result.matched_ref_id == "LAB_S001_A"


# ---------------------------------------------------------------------------
# Edge case 6: Reference is substring of query
# ---------------------------------------------------------------------------

def test_reference_substring_of_query():
    refs = ["S001"]
    result = match_single("LAB_S001_A", refs, DEFAULT_CFG)
    assert result.strategy == "substring"
    assert result.matched_ref_id == "S001"


# ---------------------------------------------------------------------------
# Edge case 7: Single character typo
# ---------------------------------------------------------------------------

def test_single_char_typo():
    result = _match("SAMPL_001")  # missing 'E'
    assert result.strategy == "fuzzy"
    assert result.matched_ref_id == "SAMPLE_001"


# ---------------------------------------------------------------------------
# Edge case 8: Transposed characters
# ---------------------------------------------------------------------------

def test_transposed_characters():
    result = _match("SMAPLE_001")  # MA→AM transposed
    assert result.strategy == "fuzzy"
    assert result.matched_ref_id == "SAMPLE_001"


# ---------------------------------------------------------------------------
# Edge case 9: Extra prefix
# ---------------------------------------------------------------------------

def test_extra_prefix():
    refs = ["SAMPLE_001"]
    result = match_single("ABC_SAMPLE_001", refs, DEFAULT_CFG)
    assert result.strategy in ("fuzzy", "substring")
    assert result.matched_ref_id == "SAMPLE_001"


# ---------------------------------------------------------------------------
# Edge case 10: Numeric padding difference
# ---------------------------------------------------------------------------

def test_numeric_padding_difference_fuzzy():
    # Without normalize_padding, fuzzy should still match
    result = _match("SAMPLE_1")
    # SAMPLE_1 vs SAMPLE_001 or SAMPLE_01 — fuzzy should pick up SAMPLE_01 (closer)
    assert result.strategy == "fuzzy"
    assert result.matched_ref_id in ("SAMPLE_01", "SAMPLE_001")


def test_numeric_padding_with_normalization():
    cfg = MatchConfig(
        use_exact=True, use_substring=False, use_fuzzy=False,
        strip_special=True, normalize_padding=True,
    )
    refs = ["SAMPLE_01"]
    result = match_single("SAMPLE_1", refs, cfg)
    assert result.strategy == "exact_norm"
    assert result.matched_ref_id == "SAMPLE_01"


# ---------------------------------------------------------------------------
# Edge case 11: No possible match
# ---------------------------------------------------------------------------

def test_no_possible_match():
    result = _match("XYZ999_UNKNOWN")
    assert result.strategy == "no_match"
    assert result.matched_ref_id is None


# ---------------------------------------------------------------------------
# Edge case 12: Empty / null query ID
# ---------------------------------------------------------------------------

def test_empty_string():
    result = _match("")
    assert result.strategy == "no_match"
    assert "empty" in result.reason.lower()


def test_nan_string():
    result = _match("nan")
    assert result.strategy == "no_match"


def test_whitespace_only():
    result = _match("   ")
    assert result.strategy == "no_match"


# ---------------------------------------------------------------------------
# Edge case 13: Duplicate IDs in reference
# ---------------------------------------------------------------------------

def test_duplicate_ids_in_reference():
    refs = ["SAMPLE_001", "SAMPLE_001", "SAMPLE_002"]
    result = match_single("SAMPLE_001", refs, DEFAULT_CFG)
    assert result.strategy == "exact"
    assert result.matched_ref_id == "SAMPLE_001"


# ---------------------------------------------------------------------------
# Edge case 14: Mixed case + extra spaces
# ---------------------------------------------------------------------------

def test_mixed_case_extra_spaces():
    result = _match("  Sample   001  ")
    # After normalizing: "sample   001" → strip spaces → could be exact_norm
    assert result.matched_ref_id in ("SAMPLE_001", "Sample_001")
    assert result.strategy in ("exact", "exact_norm", "fuzzy")


# ---------------------------------------------------------------------------
# Edge case 15: Unicode characters
# ---------------------------------------------------------------------------

def test_unicode_characters():
    refs = ["Sample_001"]
    result = match_single("Sámple_001", refs, DEFAULT_CFG)
    # After ASCII conversion: "sample_001" should match "Sample_001"
    assert result.matched_ref_id == "Sample_001"
    assert result.strategy in ("exact", "exact_norm", "fuzzy")


# ---------------------------------------------------------------------------
# Edge case 16: All-numeric ID
# ---------------------------------------------------------------------------

def test_all_numeric_id():
    result = _match("12345")
    assert result.strategy == "exact"
    assert result.matched_ref_id == "12345"


# ---------------------------------------------------------------------------
# Edge case 17: Short ID (collision risk)
# ---------------------------------------------------------------------------

def test_short_id_collision_risk():
    # "AB" is very short; should not falsely match "AB_LONG" or "ABCD"
    # with a strict fuzzy threshold it might return no_match
    cfg = MatchConfig(
        use_exact=True, use_substring=False, use_fuzzy=True,
        fuzzy_threshold=95, strip_special=True,
    )
    refs = ["AB_LONG", "ABCD"]
    result = match_single("AB", refs, cfg)
    # Either a very confident match or no match — should NOT be a low-score hit
    if result.strategy == "fuzzy":
        assert result.score >= 95
    # no_match is acceptable too


# ---------------------------------------------------------------------------
# Edge case 18: Word order difference
# ---------------------------------------------------------------------------

def test_word_order_difference():
    result = _match("Smith John")
    assert result.strategy == "fuzzy"
    assert result.matched_ref_id == "John Smith"
    assert result.score >= 80


# ---------------------------------------------------------------------------
# match_all integration
# ---------------------------------------------------------------------------

def test_match_all_basic(reference_df):
    from pandas import DataFrame
    query_ids = ["SAMPLE_001", "sample_002", "XYZ_NONE", ""]
    results = match_all(
        query_ids, reference_df, DEFAULT_CFG,
        ref_id_col="SampleID", ref_name_col="Name"
    )
    assert len(results) == 4
    strats = {r.query_id: r.strategy for r in results}
    assert strats["SAMPLE_001"] == "exact"
    assert strats["sample_002"] == "exact"
    assert strats["XYZ_NONE"] == "no_match"
    assert strats[""] == "no_match"


def test_match_all_invalid_col(reference_df):
    with pytest.raises(ValueError, match="not found"):
        match_all(["X"], reference_df, DEFAULT_CFG, ref_id_col="NONEXISTENT")
