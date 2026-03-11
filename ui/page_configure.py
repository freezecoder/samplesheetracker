from __future__ import annotations

import pandas as pd
import streamlit as st

from core.matcher import MatchConfig, MatchResult
from ui.components import callout
from ui.matching_runner import run_matching


def render_page_configure() -> None:
    st.header("Step 2 of 3 — Configure Matching")

    ref_df   = st.session_state.get("ref_df")
    query_df = st.session_state.get("query_df")

    if ref_df is None or query_df is None:
        callout("Data not loaded. Please go back to Step 1.", kind="error")
        if st.button("← Back to Load Data"):
            st.session_state["current_step"] = 1
            st.rerun()
        return

    ref_cols   = list(ref_df.columns)
    query_cols = list(query_df.columns)

    # ------------------------------------------------------------------ Column Mapping
    st.subheader("Column Mapping")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Reference Database Columns**")
        default_ref_id = _safe_index(ref_cols, st.session_state.get("ref_id_col"))
        ref_id_col = st.selectbox(
            "Sample ID column",
            ref_cols,
            index=default_ref_id,
            key="cfg_ref_id_col",
        )
        default_ref_name = _safe_index(ref_cols, st.session_state.get("ref_name_col"))
        ref_name_col = st.selectbox(
            "Sample Name column (optional)",
            ["(none)"] + ref_cols,
            index=default_ref_name + 1,
            key="cfg_ref_name_col",
        )
        if ref_name_col == "(none)":
            ref_name_col = None

    with c2:
        st.markdown("**Query Sheet Columns**")
        default_q_id = _safe_index(query_cols, st.session_state.get("query_id_col"))
        query_id_col = st.selectbox(
            "Sample ID column",
            query_cols,
            index=default_q_id,
            key="cfg_query_id_col",
        )

    # ------------------------------------------------------------------ Match Strategy
    st.subheader("Match Strategy")

    col_e, col_s, col_f = st.columns(3)
    with col_e:
        use_exact = st.checkbox(
            "Exact match",
            value=True,
            key="cfg_exact",
            help="IDs match after normalizing case & spaces",
        )
        st.caption("IDs match after normalizing case & spaces")
    with col_s:
        use_substring = st.checkbox(
            "Substring match",
            value=True,
            key="cfg_substring",
            help="Query ID appears within the reference ID, or vice versa",
        )
        st.caption("Query ID appears within the reference ID")
    with col_f:
        use_fuzzy = st.checkbox(
            "Fuzzy match",
            value=True,
            key="cfg_fuzzy",
            help="Tolerates typos and minor formatting differences",
        )
        st.caption("Tolerates typos and minor formatting diffs")

    # ------------------------------------------------------------------ Advanced Settings
    with st.expander("Advanced Settings", expanded=False):
        fuzzy_threshold = st.slider(
            "Fuzzy Score Threshold",
            min_value=0,
            max_value=100,
            value=st.session_state.get("match_config", MatchConfig()).fuzzy_threshold
            if st.session_state.get("match_config") else 80,
            key="cfg_fuzzy_threshold",
            help="Minimum similarity score required for a fuzzy match (0–100)",
        )
        strip_special = st.checkbox(
            "Strip special characters (-, _, spaces)",
            value=True,
            key="cfg_strip_special",
        )
        normalize_padding = st.checkbox(
            "Normalize numeric padding (S-1 = S-01)",
            value=False,
            key="cfg_norm_padding",
        )

        st.markdown("---")

        # ---------------------------------------------------------- Deduplication
        st.markdown("**Deduplication** (off by default)")
        dc1, dc2 = st.columns(2)
        with dc1:
            dedup_ref = st.checkbox("Dedup reference before matching", value=False, key="cfg_dedup_ref")
            if dedup_ref:
                dedup_ref_col = st.selectbox(
                    "Key column (ref)", ref_cols,
                    index=_safe_index(ref_cols, ref_id_col),
                    key="cfg_dedup_ref_col",
                )
            else:
                dedup_ref_col = ref_id_col
        with dc2:
            dedup_query = st.checkbox("Dedup query before matching", value=False, key="cfg_dedup_query")
            if dedup_query:
                dedup_query_col = st.selectbox(
                    "Key column (query)", query_cols,
                    index=_safe_index(query_cols, query_id_col),
                    key="cfg_dedup_query_col",
                )
            else:
                dedup_query_col = query_id_col

        if dedup_ref or dedup_query:
            dedup_keep = st.selectbox("Keep", ["first", "last"], key="cfg_dedup_keep")
        else:
            dedup_keep = "first"

        # Show prior dedup counts if available
        _summary = st.session_state.get("summary_stats") or {}
        if _summary.get("ref_dupes_removed"):
            st.info(f"ℹ {_summary['ref_dupes_removed']} duplicate reference row(s) removed last run")
        if _summary.get("query_dupes_removed"):
            st.info(f"ℹ {_summary['query_dupes_removed']} duplicate query row(s) removed last run")

        st.markdown("---")

        # ---------------------------------------------------------- Manual overrides
        st.markdown("#### Manual ID Mappings")
        st.info(
            "Use this table to **force-match** specific Query IDs to Reference IDs that the "
            "automated matcher couldn't resolve — for example, when the IDs use completely "
            "different naming conventions. Manual mappings are applied **first** and always "
            "win over any automated result.\n\n"
            "**How to use:**\n"
            "1. Run matching once to find unmatched IDs.\n"
            "2. Click **Pre-fill unmatched** to load them into the table.\n"
            "3. Select the correct Reference ID from the dropdown in each row.\n"
            "4. Optionally add a note explaining the mapping.\n"
            "5. Re-run matching — your mappings will be applied automatically.",
            icon="ℹ️",
        )

        # Initialise the stored mapping table from session state
        if "manual_mappings_df" not in st.session_state:
            st.session_state["manual_mappings_df"] = pd.DataFrame(
                columns=["Query ID", "Reference ID", "Notes"]
            )

        # Action buttons row
        btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 1])
        with btn_col1:
            unmatched = st.session_state.get("unmatched_df")
            n_unmatched = len(unmatched) if unmatched is not None and not unmatched.empty else 0
            prefill_label = f"Pre-fill unmatched ({n_unmatched})" if n_unmatched else "Pre-fill unmatched"
            if st.button(prefill_label, key="prefill_unmatched", disabled=(n_unmatched == 0)):
                existing = set(st.session_state["manual_mappings_df"]["Query ID"].tolist())
                new_rows = [
                    {"Query ID": qid, "Reference ID": "", "Notes": ""}
                    for qid in unmatched["Query ID"].tolist()
                    if qid not in existing
                ]
                if new_rows:
                    st.session_state["manual_mappings_df"] = pd.concat(
                        [st.session_state["manual_mappings_df"], pd.DataFrame(new_rows)],
                        ignore_index=True,
                    )
                    st.rerun()
        with btn_col2:
            active_count = len(
                st.session_state["manual_mappings_df"]
                .dropna(subset=["Reference ID"])
                .query("`Reference ID` != ''")
            )
            if active_count:
                st.markdown(f"**{active_count}** active mapping(s)")
        with btn_col3:
            if st.button("Clear all", key="clear_mappings"):
                st.session_state["manual_mappings_df"] = pd.DataFrame(
                    columns=["Query ID", "Reference ID", "Notes"]
                )
                st.rerun()

        # Build the list of valid reference IDs for validation hint
        ref_ids_list = ref_df[ref_id_col].astype(str).tolist() if ref_id_col in ref_df.columns else []

        edited = st.data_editor(
            st.session_state["manual_mappings_df"],
            num_rows="dynamic",
            use_container_width=True,
            key="manual_mappings_editor",
            column_config={
                "Query ID": st.column_config.TextColumn(
                    "Query ID",
                    help="Paste the exact ID from your query sheet",
                    required=True,
                ),
                "Reference ID": st.column_config.SelectboxColumn(
                    "Reference ID",
                    help="Choose the correct reference ID from the dropdown",
                    options=ref_ids_list,
                    required=False,
                ),
                "Notes": st.column_config.TextColumn(
                    "Notes",
                    help="Optional — explain why this mapping was needed",
                    width="medium",
                ),
            },
        )
        st.session_state["manual_mappings_df"] = edited

    # ------------------------------------------------------------------ Navigation
    st.markdown("")
    bcol, rcol = st.columns([1, 3])
    with bcol:
        if st.button("◀ Back", key="back_to_load"):
            st.session_state["current_step"] = 1
            st.rerun()
    with rcol:
        if st.button("Run Matching ▶", type="primary", key="run_matching_btn"):
            manual_mappings = _parse_manual_mappings(
                st.session_state.get("manual_mappings_df"),
                ref_df,
                ref_id_col,
                ref_name_col,
            )
            _run_matching(
                ref_df, query_df,
                ref_id_col, ref_name_col, query_id_col,
                use_exact, use_substring, use_fuzzy,
                fuzzy_threshold if use_fuzzy else 80,
                strip_special, normalize_padding,
                manual_mappings=manual_mappings,
                dedup_ref=dedup_ref,
                dedup_query=dedup_query,
                dedup_keep=dedup_keep,
                dedup_ref_key=dedup_ref_col,
                dedup_query_key=dedup_query_col,
            )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_index(options: list, value) -> int:
    try:
        return options.index(value) if value in options else 0
    except (ValueError, TypeError):
        return 0


def _parse_manual_mappings(
    df: pd.DataFrame | None,
    ref_df: pd.DataFrame,
    ref_id_col: str,
    ref_name_col: str | None,
) -> dict[str, MatchResult]:
    """
    Convert the data_editor table into a dict: query_id → MatchResult(strategy="manual").
    Only rows with both Query ID and Reference ID filled in are included.
    """
    if df is None or df.empty:
        return {}

    # Build a name lookup for the reference
    ref_name_map: dict[str, str] = {}
    if ref_name_col and ref_name_col in ref_df.columns:
        ref_name_map = dict(zip(
            ref_df[ref_id_col].astype(str),
            ref_df[ref_name_col].astype(str),
        ))

    mappings: dict[str, MatchResult] = {}
    for _, row in df.iterrows():
        qid  = str(row.get("Query ID", "")).strip()
        rid  = str(row.get("Reference ID", "")).strip()
        note = str(row.get("Notes", "")).strip()
        if qid and rid and rid.lower() not in ("", "nan", "none"):
            mappings[qid] = MatchResult(
                query_id=qid,
                matched_ref_id=rid,
                sample_name=ref_name_map.get(rid),
                strategy="manual",
                score=100.0,
                reason=note or None,
            )
    return mappings


def _run_matching(
    ref_df, query_df,
    ref_id_col, ref_name_col, query_id_col,
    use_exact, use_substring, use_fuzzy,
    fuzzy_threshold, strip_special, normalize_padding,
    manual_mappings: dict | None = None,
    dedup_ref: bool = False,
    dedup_query: bool = False,
    dedup_keep: str = "first",
    dedup_ref_key: str | None = None,
    dedup_query_key: str | None = None,
) -> None:
    config = MatchConfig(
        use_exact=use_exact,
        use_substring=use_substring,
        use_fuzzy=use_fuzzy,
        fuzzy_threshold=fuzzy_threshold,
        strip_special=strip_special,
        normalize_padding=normalize_padding,
    )
    run_matching(
        ref_df, query_df,
        ref_id_col, ref_name_col, query_id_col,
        config,
        manual_mappings=manual_mappings,
        advance_to_step3=True,
        dedup_ref=dedup_ref,
        dedup_query=dedup_query,
        dedup_keep=dedup_keep,
        dedup_ref_key=dedup_ref_key,
        dedup_query_key=dedup_query_key,
    )
