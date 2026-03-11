from __future__ import annotations

import io
from datetime import datetime

import pandas as pd
import xlsxwriter


def export_to_excel(
    matched_df: pd.DataFrame,
    unmatched_df: pd.DataFrame,
    summary: dict,
    all_results_df: pd.DataFrame | None = None,
) -> bytes:
    """Build and return a formatted .xlsx file as bytes."""
    buf = io.BytesIO()
    wb = xlsxwriter.Workbook(buf, {"in_memory": True})

    # ------------------------------------------------------------------ formats
    hdr_green  = wb.add_format({"bold": True, "bg_color": "#15803d", "font_color": "#ffffff", "border": 1})
    hdr_red    = wb.add_format({"bold": True, "bg_color": "#b91c1c", "font_color": "#ffffff", "border": 1})
    hdr_blue   = wb.add_format({"bold": True, "bg_color": "#0369a1", "font_color": "#ffffff", "border": 1})
    hdr_gray   = wb.add_format({"bold": True, "bg_color": "#475569", "font_color": "#ffffff", "border": 1})
    cell_fmt   = wb.add_format({"border": 1, "text_wrap": False})
    alt_fmt    = wb.add_format({"border": 1, "bg_color": "#f8fafc"})
    bold_fmt   = wb.add_format({"bold": True})
    label_fmt  = wb.add_format({"bold": True, "bg_color": "#e0f2fe"})
    score_good = wb.add_format({"border": 1, "bg_color": "#dcfce7", "font_color": "#14532d"})
    score_med  = wb.add_format({"border": 1, "bg_color": "#fef9c3", "font_color": "#713f12"})
    score_bad  = wb.add_format({"border": 1, "bg_color": "#fee2e2", "font_color": "#7f1d1d"})

    # ------------------------------------------------------------------ Summary
    ws = wb.add_worksheet("Summary")
    ws.set_column(0, 0, 28)
    ws.set_column(1, 1, 20)

    ws.write(0, 0, "Sample Sheet Tracker — Run Report", bold_fmt)
    ws.write(1, 0, "Generated:", label_fmt)
    ws.write(1, 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ws.write(3, 0, "Total Query Samples", label_fmt);  ws.write(3, 1, summary.get("total", 0))
    ws.write(4, 0, "Matched",             label_fmt);  ws.write(4, 1, summary.get("matched", 0))
    ws.write(5, 0, "Unmatched",           label_fmt);  ws.write(5, 1, summary.get("unmatched", 0))
    ws.write(6, 0, "Match Rate (%)",      label_fmt);  ws.write(6, 1, summary.get("match_rate", 0))

    row = 8
    ws.write(row, 0, "Matches by Strategy", bold_fmt)
    row += 1
    for strategy, count in summary.get("by_strategy", {}).items():
        ws.write(row, 0, strategy, label_fmt)
        ws.write(row, 1, count)
        row += 1

    # ------------------------------------------------------------------ Matched
    _write_df_sheet(wb, "Matched", matched_df, hdr_green, cell_fmt, alt_fmt,
                    score_col="Score", score_good=score_good, score_med=score_med, score_bad=score_bad)

    # ------------------------------------------------------------------ Unmatched
    _write_df_sheet(wb, "Unmatched", unmatched_df, hdr_red, cell_fmt, alt_fmt)

    # ------------------------------------------------------------------ All Results
    target_df = all_results_df if all_results_df is not None else pd.concat(
        [matched_df, unmatched_df], ignore_index=True
    )
    _write_df_sheet(wb, "All Results", target_df, hdr_gray, cell_fmt, alt_fmt,
                    score_col="Score", score_good=score_good, score_med=score_med, score_bad=score_bad)

    wb.close()
    return buf.getvalue()


def _write_df_sheet(
    wb, sheet_name: str, df: pd.DataFrame, hdr_fmt, cell_fmt, alt_fmt,
    score_col: str = None, score_good=None, score_med=None, score_bad=None
):
    ws = wb.add_worksheet(sheet_name)
    if df is None or df.empty:
        ws.write(0, 0, f"No {sheet_name.lower()} records.")
        return

    cols = list(df.columns)
    # Header row
    for ci, col in enumerate(cols):
        ws.write(0, ci, col, hdr_fmt)
        ws.set_column(ci, ci, max(12, len(str(col)) + 4))

    score_idx = cols.index(score_col) if score_col and score_col in cols else None

    for ri, (_, row) in enumerate(df.iterrows(), start=1):
        fmt = alt_fmt if ri % 2 == 0 else cell_fmt
        for ci, col in enumerate(cols):
            val = row[col]
            if pd.isna(val) or val == "":
                ws.write(ri, ci, "", fmt)
            elif score_idx is not None and ci == score_idx and isinstance(val, (int, float)):
                if val >= 90:
                    ws.write(ri, ci, val, score_good)
                elif val >= 70:
                    ws.write(ri, ci, val, score_med)
                else:
                    ws.write(ri, ci, val, score_bad)
            else:
                ws.write(ri, ci, str(val), fmt)
