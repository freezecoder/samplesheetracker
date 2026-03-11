from __future__ import annotations

import random
import string
import streamlit as st
import pandas as pd
from datetime import datetime

from core.excel_exporter import export_to_excel
from ui.components import callout, render_metric_row, score_badge


def _suggested_filename() -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = "".join(random.choices(string.ascii_lowercase, k=4))
    return f"results_{ts}_{suffix}.xlsx"


def render_page_results(expert_mode: bool = False) -> None:
    if expert_mode:
        st.header("Results")
    else:
        st.header("Step 3 of 3 — Results")

    summary      = st.session_state.get("summary_stats")
    matched_df   = st.session_state.get("matched_df")
    unmatched_df = st.session_state.get("unmatched_df")
    results_df   = st.session_state.get("results_df")

    if summary is None or results_df is None:
        if expert_mode:
            st.info("Load data and configure settings in the sidebar, then click **Run**.")
        else:
            callout("No results available. Please run matching first.", kind="warning")
            if st.button("← Back to Configure"):
                st.session_state["current_step"] = 2
                st.rerun()
        return

    # ------------------------------------------------------------------ Metric cards
    render_metric_row(summary)
    st.markdown("")

    # ------------------------------------------------------------------ Strategy breakdown (inline)
    if summary.get("by_strategy"):
        with st.expander("Match Strategy Breakdown", expanded=False):
            strategy_data = [
                {"Strategy": k, "Count": v}
                for k, v in summary["by_strategy"].items()
            ]
            st.dataframe(
                pd.DataFrame(strategy_data),
                use_container_width=True,
                hide_index=True,
            )

    # ------------------------------------------------------------------ Results tabs
    tab_matched, tab_unmatched = st.tabs([
        f"✓ Matched Samples  ({summary.get('matched', 0)})",
        f"✗ Unmatched  ({summary.get('unmatched', 0)})",
    ])

    with tab_matched:
        _render_matched_tab(matched_df)

    with tab_unmatched:
        _render_unmatched_tab(unmatched_df)

    # ------------------------------------------------------------------ Download
    st.markdown("")
    st.markdown("---")
    _render_download_section(matched_df, unmatched_df, summary, results_df)

    # ------------------------------------------------------------------ Navigation
    if not expert_mode:
        if st.button("← Back to Configure", key="back_to_config"):
            st.session_state["current_step"] = 2
            st.rerun()


# ---------------------------------------------------------------------------
# Matched tab
# ---------------------------------------------------------------------------

def _render_matched_tab(df: pd.DataFrame | None) -> None:
    if df is None or df.empty:
        st.info("No matched samples.")
        return

    # Search + filter controls
    c1, c2 = st.columns([3, 2])
    with c1:
        search = st.text_input(
            "Search matched results",
            placeholder="Search by Query ID, Ref ID, or Name…",
            key="matched_search",
            label_visibility="collapsed",
        )
    with c2:
        if "Strategy" in df.columns:
            strategies = ["All"] + sorted(df["Strategy"].dropna().unique().tolist())
            strategy_filter = st.selectbox(
                "Filter by Strategy",
                strategies,
                key="matched_strategy_filter",
                label_visibility="collapsed",
            )
        else:
            strategy_filter = "All"

    filtered = df.copy()

    if search:
        mask = pd.Series(False, index=filtered.index)
        for col in ["Query ID", "Matched ID", "Sample Name"]:
            if col in filtered.columns:
                mask |= filtered[col].astype(str).str.contains(search, case=False, na=False)
        filtered = filtered[mask]

    if strategy_filter != "All" and "Strategy" in filtered.columns:
        filtered = filtered[filtered["Strategy"] == strategy_filter]

    # Render with score badges via HTML or plain dataframe
    st.markdown(
        f'<div aria-live="polite">Showing {len(filtered):,} of {len(df):,} matched samples</div>',
        unsafe_allow_html=True,
    )
    _display_results_table(filtered)


def _render_unmatched_tab(df: pd.DataFrame | None) -> None:
    if df is None or df.empty:
        st.success("All samples matched successfully!")
        return

    st.markdown(
        '<div class="callout-warning" role="alert">'
        f'<strong>⚠</strong> {len(df)} sample(s) could not be matched. '
        'Review the reasons below and consider adjusting your settings.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    search = st.text_input(
        "Search unmatched",
        placeholder="Search by Query ID…",
        key="unmatched_search",
        label_visibility="collapsed",
    )
    filtered = df.copy()
    if search:
        mask = filtered["Query ID"].astype(str).str.contains(search, case=False, na=False)
        filtered = filtered[mask]

    st.dataframe(filtered, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _display_results_table(df: pd.DataFrame) -> None:
    """Display results using st.dataframe with pagination."""
    PAGE_SIZE = 25
    total = len(df)
    n_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    if n_pages > 1:
        page = st.number_input(
            f"Page (1–{n_pages})",
            min_value=1,
            max_value=n_pages,
            value=1,
            step=1,
            key="matched_page",
        )
    else:
        page = 1

    start = (page - 1) * PAGE_SIZE
    end   = start + PAGE_SIZE
    page_df = df.iloc[start:end].copy()

    # Style Score column
    if "Score" in page_df.columns:
        def _style_score(val):
            if val == "" or pd.isna(val):
                return ""
            try:
                v = float(val)
            except (ValueError, TypeError):
                return ""
            if v >= 90:
                return "background-color: #dcfce7; color: #14532d; font-weight: 600"
            elif v >= 70:
                return "background-color: #fef9c3; color: #713f12; font-weight: 600"
            else:
                return "background-color: #fee2e2; color: #7f1d1d; font-weight: 600"

        styled = page_df.style.applymap(_style_score, subset=["Score"])
        st.dataframe(styled, use_container_width=True, hide_index=True)
    else:
        st.dataframe(page_df, use_container_width=True, hide_index=True)

    if n_pages > 1:
        st.caption(f"Showing {start+1}–{min(end, total)} of {total:,}")


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

def _render_download_section(matched_df, unmatched_df, summary, all_results_df) -> None:
    st.subheader("Download Results")

    export_matched   = matched_df    if matched_df   is not None else pd.DataFrame()
    export_unmatched = unmatched_df  if unmatched_df is not None else pd.DataFrame()

    # Filename input — suggest a name, let user override
    if "download_filename" not in st.session_state:
        st.session_state["download_filename"] = _suggested_filename()

    fn_col, btn_col = st.columns([3, 2])
    with fn_col:
        filename = st.text_input(
            "File name",
            value=st.session_state["download_filename"],
            key="download_filename_input",
            label_visibility="collapsed",
            placeholder="results_YYYYMMDD_HHMMSS_xxxx.xlsx",
        )
        if not filename.endswith(".xlsx"):
            filename = filename.rstrip(".") + ".xlsx"

    try:
        xlsx_bytes = export_to_excel(
            export_matched,
            export_unmatched,
            summary,
            all_results_df=all_results_df,
        )
        with btn_col:
            st.download_button(
                label="⬇ Download (.xlsx)",
                data=xlsx_bytes,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                key="download_xlsx",
            )
        st.caption("Excel file includes: Summary, Matched, Unmatched, and All Results sheets.")
    except Exception as e:
        callout(f"Export failed: {e}", kind="error")
