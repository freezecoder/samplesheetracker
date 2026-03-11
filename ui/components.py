"""Reusable UI widgets: badges, metric cards, callouts."""
from __future__ import annotations

import streamlit as st


def score_badge(score: float | str, strategy: str) -> str:
    """Return an HTML badge string for a match score."""
    if strategy in ("Exact", "Normalized Exact"):
        return f'<span class="badge badge-neutral" aria-label="Exact match">Exact</span>'
    if strategy == "Substring":
        return f'<span class="badge badge-neutral" aria-label="Substring match">Sub</span>'
    if isinstance(score, (int, float)):
        if score >= 90:
            css = "badge-green"
        elif score >= 70:
            css = "badge-amber"
        else:
            css = "badge-red"
        return f'<span class="badge {css}" aria-label="Fuzzy score {score:.0f}">{score:.0f}</span>'
    return f'<span class="badge badge-neutral">{score}</span>'


def metric_card(label: str, value: str | int | float, sub: str = "") -> str:
    """Return an HTML metric card."""
    sub_html = f'<div style="font-size:12px;opacity:0.7;margin-top:2px">{sub}</div>' if sub else ""
    return f"""
    <div class="metric-card">
        <div style="font-size:28px;font-weight:700;line-height:1.2">{value}</div>
        <div style="font-size:13px;margin-top:4px">{label}</div>
        {sub_html}
    </div>
    """


def callout(message: str, kind: str = "success") -> None:
    """Render a styled callout block (success / warning / error)."""
    icons = {"success": "✓", "warning": "⚠", "error": "✗"}
    icon = icons.get(kind, "")
    role = "alert" if kind in ("warning", "error") else "status"
    st.markdown(
        f'<div class="callout-{kind}" role="{role}" aria-live="polite">'
        f'<strong>{icon}</strong> {message}</div>',
        unsafe_allow_html=True,
    )


def render_metric_row(stats: dict) -> None:
    """Render four metric cards in a row."""
    cols = st.columns(4)
    cards = [
        ("Total Samples", stats.get("total", 0), ""),
        ("Matched",       stats.get("matched", 0), ""),
        ("Unmatched",     stats.get("unmatched", 0), ""),
        ("Match Rate",    f"{stats.get('match_rate', 0):.1f}%", ""),
    ]
    for col, (label, val, sub) in zip(cols, cards):
        with col:
            st.markdown(metric_card(label, val, sub), unsafe_allow_html=True)


def file_preview_card(filename: str, row_count: int, columns: list[str], df) -> None:
    """Display a post-upload validation card with a data preview."""
    cols_str = ", ".join(str(c) for c in columns[:6])
    if len(columns) > 6:
        cols_str += f" … +{len(columns)-6} more"
    st.markdown(
        f'<div class="callout-success"><strong>✓ {filename}</strong> — '
        f'{row_count:,} rows &nbsp;|&nbsp; Columns: {cols_str}</div>',
        unsafe_allow_html=True,
    )
    if df is not None and not df.empty:
        st.dataframe(df.head(3), use_container_width=True, hide_index=True)
