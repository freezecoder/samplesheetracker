from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from themes import get_theme_css
from ui.stepper import render_stepper

LOGO_PATH = Path(__file__).parent.parent / "assets" / "logo_placeholder.png"


def render_sidebar() -> None:
    """Render the persistent sidebar."""
    with st.sidebar:
        _render_logo()

        # Mode toggle — always visible, just below logo
        app_mode = st.radio(
            "Mode",
            ["Wizard", "Expert"],
            horizontal=True,
            key="app_mode",
            label_visibility="collapsed",
        )

        st.divider()

        if app_mode == "Expert":
            _render_expert_sidebar()
        else:
            _render_wizard_sidebar()

        st.divider()
        _render_theme_selector()
        st.markdown("---")
        if st.button("↺ Start Over", key="start_over_btn", use_container_width=True):
            _reset_session()
            st.rerun()


# ---------------------------------------------------------------------------
# Wizard sidebar (original behaviour)
# ---------------------------------------------------------------------------

def _render_wizard_sidebar() -> None:
    _render_stepper_section()
    st.divider()
    _render_session_status()

    if st.session_state.get("current_step") == 3 and st.session_state.get("ref_df") is not None:
        st.divider()
        _render_rerun_panel()


def _render_stepper_section() -> None:
    st.markdown("**PROGRESS**")
    current = st.session_state.get("current_step", 1)
    render_stepper(current, steps=["Load", "Config", "Results"])


def _render_session_status() -> None:
    st.markdown("**SESSION STATUS**")
    ref_df   = st.session_state.get("ref_df")
    query_df = st.session_state.get("query_df")
    summary  = st.session_state.get("summary_stats")
    results  = st.session_state.get("results_df")

    ref_label = f"✓ {len(ref_df):,} rows" if ref_df is not None else "— not loaded"
    q_label   = f"✓ {len(query_df):,} rows" if query_df is not None else "— not loaded"
    if summary:
        res_label = f"✓ {summary['matched']}/{summary['total']}  ({summary['match_rate']}%)"
    elif results is not None:
        res_label = f"✓ {len(results)} rows"
    else:
        res_label = "—"

    st.caption(f"Reference:  {ref_label}")
    st.caption(f"Query:      {q_label}")
    st.caption(f"Results:    {res_label}")


def _render_rerun_panel() -> None:
    """Compact match-settings panel that lets the user re-run without leaving Step 3."""
    from core.matcher import MatchConfig
    from ui.matching_runner import run_matching

    st.markdown("**MATCH SETTINGS**")

    cfg: MatchConfig = st.session_state.get("match_config") or MatchConfig()

    use_exact     = st.checkbox("Exact",     value=cfg.use_exact,     key="sb_exact")
    use_substring = st.checkbox("Substring", value=cfg.use_substring, key="sb_substring")
    use_fuzzy     = st.checkbox("Fuzzy",     value=cfg.use_fuzzy,     key="sb_fuzzy")

    fuzzy_threshold = st.slider(
        "Fuzzy threshold",
        min_value=0,
        max_value=100,
        value=cfg.fuzzy_threshold,
        step=5,
        key="sb_fuzzy_threshold",
        disabled=not use_fuzzy,
    )

    strip_special    = st.checkbox("Strip -, _, spaces", value=cfg.strip_special,      key="sb_strip")
    normalize_padding = st.checkbox("Normalize padding",  value=cfg.normalize_padding,  key="sb_norm_pad")

    # Dedup options
    st.markdown("**Deduplication**")
    _sb_ref_df   = st.session_state.get("ref_df")
    _sb_query_df = st.session_state.get("query_df")
    _sb_ref_id   = st.session_state.get("ref_id_col") or ""
    _sb_query_id = st.session_state.get("query_id_col") or ""
    _sb_ref_cols   = list(_sb_ref_df.columns)   if _sb_ref_df   is not None else [_sb_ref_id]
    _sb_query_cols = list(_sb_query_df.columns) if _sb_query_df is not None else [_sb_query_id]

    sb_dedup_ref = st.checkbox("Dedup reference", value=False, key="sb_dedup_ref")
    if sb_dedup_ref:
        sb_dedup_ref_key = st.selectbox(
            "Key column (ref)", _sb_ref_cols,
            index=_safe_index(_sb_ref_cols, _sb_ref_id),
            key="sb_dedup_ref_key",
        )
    else:
        sb_dedup_ref_key = _sb_ref_id

    sb_dedup_query = st.checkbox("Dedup query", value=False, key="sb_dedup_query")
    if sb_dedup_query:
        sb_dedup_query_key = st.selectbox(
            "Key column (query)", _sb_query_cols,
            index=_safe_index(_sb_query_cols, _sb_query_id),
            key="sb_dedup_query_key",
        )
    else:
        sb_dedup_query_key = _sb_query_id

    if sb_dedup_ref or sb_dedup_query:
        sb_dedup_keep = st.selectbox("Keep", ["first", "last"], key="sb_dedup_keep")
    else:
        sb_dedup_keep = "first"

    # Manual mappings count (read-only)
    manual_df = st.session_state.get("manual_mappings_df")
    if manual_df is not None and not manual_df.empty:
        active = manual_df.dropna(subset=["Reference ID"]).query("`Reference ID` != ''")
        if not active.empty:
            st.caption(f"{len(active)} manual override(s) active")

    st.markdown("")
    if st.button("⟳ Re-run Matching", type="primary", key="sb_rerun_btn", use_container_width=True):
        ref_df       = st.session_state.get("ref_df")
        query_df     = st.session_state.get("query_df")
        ref_id_col   = st.session_state.get("ref_id_col")
        ref_name_col = st.session_state.get("ref_name_col")
        query_id_col = st.session_state.get("query_id_col")

        if ref_df is None or query_df is None or not ref_id_col or not query_id_col:
            st.error("Missing data — go back to Step 1.")
            return

        new_config = MatchConfig(
            use_exact=use_exact,
            use_substring=use_substring,
            use_fuzzy=use_fuzzy,
            fuzzy_threshold=fuzzy_threshold,
            strip_special=strip_special,
            normalize_padding=normalize_padding,
        )

        from ui.page_configure import _parse_manual_mappings
        manual_mappings = _parse_manual_mappings(
            st.session_state.get("manual_mappings_df"),
            ref_df, ref_id_col, ref_name_col,
        )

        run_matching(
            ref_df, query_df,
            ref_id_col, ref_name_col, query_id_col,
            new_config,
            manual_mappings=manual_mappings,
            advance_to_step3=False,
            dedup_ref=sb_dedup_ref,
            dedup_query=sb_dedup_query,
            dedup_keep=sb_dedup_keep,
            dedup_ref_key=sb_dedup_ref_key,
            dedup_query_key=sb_dedup_query_key,
        )


# ---------------------------------------------------------------------------
# Expert sidebar
# ---------------------------------------------------------------------------

def _render_expert_sidebar() -> None:
    ref_df   = st.session_state.get("ref_df")
    query_df = st.session_state.get("query_df")
    results  = st.session_state.get("results_df")
    summary  = st.session_state.get("summary_stats")

    # ------------------------------------------------------------------ Section 1: DATA
    with st.expander("DATA", expanded=(ref_df is None or query_df is None)):
        from core.data_loader import (
            load_reference_from_file, load_query_sheet,
            get_sheet_names, detect_id_column, detect_name_column,
        )
        from config.defaults import DEFAULT_ID_COLUMN_CANDIDATES, DEFAULT_NAME_COLUMN_CANDIDATES

        st.markdown("**Reference**")
        ref_mode = st.radio(
            "ref_mode", ["Upload file", "Folder path"],
            horizontal=True, key="exp_ref_mode", label_visibility="collapsed",
        )
        if ref_mode == "Upload file":
            uploaded_ref = st.file_uploader(
                "Reference file", type=["xlsx", "xls", "csv"],
                key="exp_ref_upload", label_visibility="collapsed",
            )
            if uploaded_ref is not None:
                sheet = 0
                if not uploaded_ref.name.endswith(".csv"):
                    snames = get_sheet_names(uploaded_ref)
                    if len(snames) > 1:
                        sel = st.selectbox("Sheet", snames, key="exp_ref_sheet")
                        sheet = snames.index(sel)
                    uploaded_ref.seek(0)
                try:
                    df = load_reference_from_file(uploaded_ref, sheet_name=sheet)
                    st.session_state["ref_df"] = df
                    st.session_state["ref_filename"] = uploaded_ref.name
                    _expert_auto_detect(df, "ref", DEFAULT_ID_COLUMN_CANDIDATES, DEFAULT_NAME_COLUMN_CANDIDATES)
                    ref_df = df
                except Exception as e:
                    st.error(f"Failed: {e}")
        else:
            folder = st.text_input("Folder path", key="exp_ref_folder", placeholder="/path/to/folder")
            if st.button("Load folder", key="exp_ref_folder_btn"):
                from core.data_loader import load_reference_from_folder
                try:
                    df = load_reference_from_folder(folder)
                    st.session_state["ref_df"] = df
                    st.session_state["ref_filename"] = f"Folder: {folder}"
                    _expert_auto_detect(df, "ref", DEFAULT_ID_COLUMN_CANDIDATES, DEFAULT_NAME_COLUMN_CANDIDATES)
                    ref_df = df
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")

        if ref_df is not None:
            cols_preview = ", ".join(list(ref_df.columns)[:4])
            st.caption(f"✓ {len(ref_df):,} rows — {cols_preview}")

        st.markdown("**Query**")
        uploaded_query = st.file_uploader(
            "Query file", type=["xlsx", "xls", "csv"],
            key="exp_query_upload", label_visibility="collapsed",
        )
        if uploaded_query is not None:
            sheet = 0
            if not uploaded_query.name.endswith(".csv"):
                snames = get_sheet_names(uploaded_query)
                if len(snames) > 1:
                    sel = st.selectbox("Sheet (query)", snames, key="exp_query_sheet")
                    sheet = snames.index(sel)
                uploaded_query.seek(0)
            try:
                df = load_query_sheet(uploaded_query, sheet_name=sheet)
                st.session_state["query_df"] = df
                st.session_state["query_filename"] = uploaded_query.name
                _expert_auto_detect(df, "query", DEFAULT_ID_COLUMN_CANDIDATES, DEFAULT_NAME_COLUMN_CANDIDATES)
                query_df = df
            except Exception as e:
                st.error(f"Failed: {e}")

        if query_df is not None:
            cols_preview = ", ".join(list(query_df.columns)[:4])
            st.caption(f"✓ {len(query_df):,} rows — {cols_preview}")

    # ------------------------------------------------------------------ Section 2: COLUMNS
    with st.expander("COLUMNS", expanded=(ref_df is not None and query_df is not None and results is None)):
        if ref_df is None or query_df is None:
            st.caption("Load data first.")
        else:
            ref_cols   = list(ref_df.columns)
            query_cols = list(query_df.columns)

            exp_ref_id_col = st.selectbox(
                "Ref ID column", ref_cols,
                index=_safe_index(ref_cols, st.session_state.get("ref_id_col")),
                key="exp_ref_id_col",
            )
            exp_ref_name_col = st.selectbox(
                "Ref Name column (optional)", ["(none)"] + ref_cols,
                index=_safe_index_offset(ref_cols, st.session_state.get("ref_name_col")),
                key="exp_ref_name_col",
            )
            exp_query_id_col = st.selectbox(
                "Query ID column", query_cols,
                index=_safe_index(query_cols, st.session_state.get("query_id_col")),
                key="exp_query_id_col",
            )

    # ------------------------------------------------------------------ Section 3: MATCH SETTINGS
    from core.matcher import MatchConfig
    cfg: MatchConfig = st.session_state.get("match_config") or MatchConfig()

    with st.expander("MATCH SETTINGS", expanded=True):
        exp_exact     = st.checkbox("Exact",     value=cfg.use_exact,     key="exp_exact")
        exp_substring = st.checkbox("Substring", value=cfg.use_substring, key="exp_substring")
        exp_fuzzy     = st.checkbox("Fuzzy",     value=cfg.use_fuzzy,     key="exp_fuzzy")
        exp_threshold = st.slider(
            "Fuzzy threshold", 0, 100, value=cfg.fuzzy_threshold, step=5,
            key="exp_threshold", disabled=not exp_fuzzy,
        )
        exp_strip    = st.checkbox("Strip -, _, spaces", value=cfg.strip_special,     key="exp_strip")
        exp_norm_pad = st.checkbox("Normalize padding",  value=cfg.normalize_padding, key="exp_norm_pad")

    # ------------------------------------------------------------------ Section 4: DEDUPLICATION
    _exp_ref_cols   = list(ref_df.columns)   if ref_df   is not None else []
    _exp_query_cols = list(query_df.columns) if query_df is not None else []
    _exp_ref_id_default   = st.session_state.get("exp_ref_id_col")   or st.session_state.get("ref_id_col")   or ""
    _exp_query_id_default = st.session_state.get("exp_query_id_col") or st.session_state.get("query_id_col") or ""

    with st.expander("DEDUPLICATION", expanded=False):
        st.caption("Remove duplicate rows before matching, keeping the first or last occurrence.")
        exp_dedup_ref = st.checkbox("Dedup reference", value=False, key="exp_dedup_ref")
        if exp_dedup_ref and _exp_ref_cols:
            exp_dedup_ref_key = st.selectbox(
                "Key column (ref)", _exp_ref_cols,
                index=_safe_index(_exp_ref_cols, _exp_ref_id_default),
                key="exp_dedup_ref_key",
            )
        else:
            exp_dedup_ref_key = _exp_ref_id_default

        exp_dedup_query = st.checkbox("Dedup query", value=False, key="exp_dedup_query")
        if exp_dedup_query and _exp_query_cols:
            exp_dedup_query_key = st.selectbox(
                "Key column (query)", _exp_query_cols,
                index=_safe_index(_exp_query_cols, _exp_query_id_default),
                key="exp_dedup_query_key",
            )
        else:
            exp_dedup_query_key = _exp_query_id_default

        if exp_dedup_ref or exp_dedup_query:
            exp_dedup_keep = st.selectbox("Keep", ["first", "last"], key="exp_dedup_keep")
        else:
            exp_dedup_keep = "first"

        _summary_ded = st.session_state.get("summary_stats") or {}
        if _summary_ded.get("ref_dupes_removed"):
            st.info(f"ℹ {_summary_ded['ref_dupes_removed']} ref dupe(s) removed last run")
        if _summary_ded.get("query_dupes_removed"):
            st.info(f"ℹ {_summary_ded['query_dupes_removed']} query dupe(s) removed last run")

    # ------------------------------------------------------------------ Section 5: MANUAL MAPPINGS
    with st.expander("MANUAL MAPPINGS", expanded=False):
        st.caption(
            "Force-match Query IDs to Reference IDs the matcher couldn't resolve. "
            "These override automated results. Run matching first, then pre-fill unmatched rows."
        )

        if "manual_mappings_df" not in st.session_state:
            st.session_state["manual_mappings_df"] = pd.DataFrame(
                columns=["Query ID", "Reference ID", "Notes"]
            )

        _cur_ref_df = st.session_state.get("ref_df")
        _cur_ref_id = st.session_state.get("exp_ref_id_col") or st.session_state.get("ref_id_col")
        ref_ids_list = []
        if _cur_ref_df is not None and _cur_ref_id and _cur_ref_id in _cur_ref_df.columns:
            ref_ids_list = _cur_ref_df[_cur_ref_id].astype(str).tolist()

        edited = st.data_editor(
            st.session_state["manual_mappings_df"],
            num_rows="dynamic",
            use_container_width=True,
            key="exp_manual_mappings_editor",
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
                ),
            },
        )
        st.session_state["manual_mappings_df"] = edited

        _exp_active_count = len(
            edited.dropna(subset=["Reference ID"]).query("`Reference ID` != ''")
        )
        if _exp_active_count:
            st.caption(f"**{_exp_active_count}** active mapping(s)")

        _unmatched = st.session_state.get("unmatched_df")
        n_unmatched = len(_unmatched) if _unmatched is not None and not _unmatched.empty else 0
        btn_a, btn_b = st.columns(2)
        with btn_a:
            prefill_lbl = f"Pre-fill unmatched ({n_unmatched})" if n_unmatched else "Pre-fill unmatched"
            if st.button(prefill_lbl, key="exp_prefill_unmatched", disabled=(n_unmatched == 0)):
                existing = set(st.session_state["manual_mappings_df"]["Query ID"].tolist())
                new_rows = [
                    {"Query ID": qid, "Reference ID": "", "Notes": ""}
                    for qid in _unmatched["Query ID"].tolist()
                    if qid not in existing
                ]
                if new_rows:
                    st.session_state["manual_mappings_df"] = pd.concat(
                        [st.session_state["manual_mappings_df"], pd.DataFrame(new_rows)],
                        ignore_index=True,
                    )
                    st.rerun()
        with btn_b:
            if st.button("Clear all", key="exp_clear_mappings"):
                st.session_state["manual_mappings_df"] = pd.DataFrame(
                    columns=["Query ID", "Reference ID", "Notes"]
                )
                st.rerun()

    # ------------------------------------------------------------------ Actions
    st.markdown("")
    run_label = "⟳ Re-run" if results is not None else "▶ Run"
    if st.button(run_label, type="primary", use_container_width=True, key="exp_run_btn"):
        _exp_ref_df   = st.session_state.get("ref_df")
        _exp_query_df = st.session_state.get("query_df")
        _exp_ref_id   = st.session_state.get("exp_ref_id_col") or st.session_state.get("ref_id_col")
        _exp_ref_name = st.session_state.get("exp_ref_name_col") or st.session_state.get("ref_name_col")
        _exp_query_id = st.session_state.get("exp_query_id_col") or st.session_state.get("query_id_col")

        if _exp_ref_name == "(none)":
            _exp_ref_name = None

        if _exp_ref_df is None or _exp_query_df is None or not _exp_ref_id or not _exp_query_id:
            st.error("Load data and set columns before running.")
        else:
            new_config = MatchConfig(
                use_exact=exp_exact,
                use_substring=exp_substring,
                use_fuzzy=exp_fuzzy,
                fuzzy_threshold=exp_threshold if exp_fuzzy else 80,
                strip_special=exp_strip,
                normalize_padding=exp_norm_pad,
            )

            from ui.page_configure import _parse_manual_mappings
            from ui.matching_runner import run_matching
            manual_mappings = _parse_manual_mappings(
                st.session_state.get("manual_mappings_df"),
                _exp_ref_df, _exp_ref_id, _exp_ref_name,
            )

            # Persist column choices to session state for use by page_results
            st.session_state["ref_id_col"]   = _exp_ref_id
            st.session_state["ref_name_col"] = _exp_ref_name
            st.session_state["query_id_col"] = _exp_query_id

            run_matching(
                _exp_ref_df, _exp_query_df,
                _exp_ref_id, _exp_ref_name, _exp_query_id,
                new_config,
                manual_mappings=manual_mappings,
                advance_to_step3=False,
                dedup_ref=exp_dedup_ref,
                dedup_query=exp_dedup_query,
                dedup_keep=exp_dedup_keep,
                dedup_ref_key=exp_dedup_ref_key,
                dedup_query_key=exp_dedup_query_key,
            )

    if results is not None:
        _exp_matched   = st.session_state.get("matched_df", pd.DataFrame())
        _exp_unmatched = st.session_state.get("unmatched_df", pd.DataFrame())
        try:
            from core.excel_exporter import export_to_excel
            from ui.page_results import _suggested_filename
            xlsx_bytes = export_to_excel(
                _exp_matched, _exp_unmatched, summary or {},
                all_results_df=results,
            )
            if "download_filename" not in st.session_state:
                st.session_state["download_filename"] = _suggested_filename()
            exp_filename = st.text_input(
                "File name",
                value=st.session_state["download_filename"],
                key="exp_download_filename",
                label_visibility="collapsed",
            )
            if not exp_filename.endswith(".xlsx"):
                exp_filename = exp_filename.rstrip(".") + ".xlsx"
            st.download_button(
                label="⬇ Download .xlsx",
                data=xlsx_bytes,
                file_name=exp_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="exp_download_btn",
            )
        except Exception:
            pass

    # Compact status caption
    if ref_df is not None or query_df is not None or summary is not None:
        parts = []
        if ref_df is not None:
            parts.append(f"Ref {len(ref_df):,}r")
        if query_df is not None:
            parts.append(f"Query {len(query_df):,}r")
        if summary:
            parts.append(f"{summary['matched']}/{summary['total']} {summary['match_rate']}%")
        st.caption(" · ".join(parts))


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _expert_auto_detect(df, prefix: str, id_candidates, name_candidates) -> None:
    from core.data_loader import detect_id_column, detect_name_column
    id_col   = detect_id_column(df, id_candidates)
    name_col = detect_name_column(df, name_candidates)
    if prefix == "ref":
        if id_col:
            st.session_state["ref_id_col"] = id_col
        if name_col:
            st.session_state["ref_name_col"] = name_col
    elif prefix == "query":
        if id_col:
            st.session_state["query_id_col"] = id_col


def _safe_index(options: list, value) -> int:
    try:
        return options.index(value) if value in options else 0
    except (ValueError, TypeError):
        return 0


def _safe_index_offset(options: list, value) -> int:
    """Index into a list prepended with '(none)', so 0 = none, 1+ = options."""
    if value is None or value not in options:
        return 0
    try:
        return options.index(value) + 1
    except (ValueError, TypeError):
        return 0


def inject_theme_css() -> None:
    theme = st.session_state.get("theme", "Light")
    st.markdown(get_theme_css(theme), unsafe_allow_html=True)


def _render_logo() -> None:
    col_logo, col_title = st.columns([1, 3])
    with col_logo:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=48)
        else:
            st.markdown(
                '<div style="font-size:32px;line-height:1" aria-label="App logo">🧬</div>',
                unsafe_allow_html=True,
            )
    with col_title:
        st.markdown("**Sample Sheet Tracker**")
        st.caption("v1.0")


def _render_theme_selector() -> None:
    current_theme = st.session_state.get("theme", "Light")
    theme = st.selectbox(
        "Theme",
        ["Light", "Beige", "Dark"],
        index=["Light", "Beige", "Dark"].index(current_theme),
        key="theme_select",
        label_visibility="visible",
    )
    if theme != st.session_state.get("theme"):
        st.session_state["theme"] = theme
        st.rerun()


def _reset_session() -> None:
    keys = [
        "current_step", "ref_df", "query_df", "ref_filename", "query_filename",
        "ref_id_col", "ref_name_col", "query_id_col", "match_config",
        "results_df", "matched_df", "unmatched_df", "summary_stats",
        "manual_mappings_df",
    ]
    for k in keys:
        st.session_state.pop(k, None)
