import streamlit as st


def render_page_userguide() -> None:
    st.header("User Guide")
    st.markdown(
        "Everything you need to use Sample Sheet Tracker effectively. "
        "Expand any section below."
    )

    # ------------------------------------------------------------------ Overview
    with st.expander("What does this app do?", expanded=True):
        st.markdown("""
Sample Sheet Tracker finds which samples in your query sheet exist in a reference database —
even when IDs are formatted differently across systems, operators, or instruments.

**Common problems it solves:**

| Problem | Example |
|---------|---------|
| Separator differences | `SAMPLE-001` vs `SAMPLE_001` vs `SAMPLE 001` |
| Missing leading zeros | `S-1` vs `S-01` vs `S-001` |
| Typos / transpositions | `SAMPL_001` vs `SAMPLE_001` |
| Word-order differences | `ALPHA-PT-015` vs `PT-ALPHA-015` |
| Operator-added prefixes | `LAB_S001` vs `S001` |
| Unicode / copy-paste artefacts | Non-breaking hyphens, accented characters |

**Workflow in three steps:**
1. Upload your reference database and query sheet
2. Configure which columns to match and which strategies to use
3. Download a formatted Excel report showing every match and every failure
        """)

    # ------------------------------------------------------------------ Modes
    with st.expander("Wizard Mode vs Expert Mode"):
        st.markdown("""
The **mode toggle** in the top of the sidebar switches between two interfaces.
Your loaded data and results are preserved when you switch — nothing is reset.

---

### Wizard Mode (default)

A guided three-step flow:

**Step 1 — Load Data**
Upload your reference database and query sheet. The app detects ID columns automatically.

**Step 2 — Configure Matching**
Select the ID columns, choose match strategies, and optionally configure deduplication and manual mappings.

**Step 3 — Results**
View summary cards, browse matched and unmatched samples, and download the Excel report.
A re-run panel in the sidebar lets you adjust settings and re-run without going back to Step 2.

---

### Expert Mode

All controls collapse into the sidebar. The main panel always shows results.
Designed for power users who need rapid iteration.

**Sidebar sections:**
- **DATA** — Upload files or load from a folder path
- **COLUMNS** — Pick the ID and name columns for each file
- **MATCH SETTINGS** — Strategies, fuzzy threshold, normalization
- **DEDUPLICATION** — Remove duplicates before matching
- **MANUAL MAPPINGS** — Force-match specific IDs

Click **▶ Run** to run, **⟳ Re-run** after results are visible to iterate.
        """)

    # ------------------------------------------------------------------ Step 1: Loading data
    with st.expander("Loading Your Data"):
        st.markdown("""
### Reference Database

The master list of all known samples — the "source of truth."

- Upload a single `.xlsx`, `.xls`, or `.csv` file, **or**
- Specify a folder path — all matching files in the folder are concatenated into one database

### Query Sheet

The list of sample IDs you want to look up. Usually a smaller file from an instrument or collaborator.

- Upload a single `.xlsx`, `.xls`, or `.csv` file

### Tips

- **Multi-sheet Excel files**: a sheet selector appears automatically — pick the right sheet.
- **Auto-detection**: the app scans column names for keywords like `SampleID`, `ID`, `Barcode`,
  `AccessionID`, `SpecimenID`, etc. If detection is wrong, override it in Step 2 / COLUMNS.
- **Preview**: a preview card shows the first few rows after upload so you can verify.
- **Example datasets**: use the "Try with example data" expander on Step 1 to load one of
  four built-in challenging datasets covering common real-world ID problems.
        """)

    # ------------------------------------------------------------------ Step 2: Configuring
    with st.expander("Configuring Matching"):
        st.markdown("""
### Column Mapping

Select which column in each file contains the sample IDs.

| Field | Purpose |
|-------|---------|
| **Reference ID column** | The unique identifier in your reference database |
| **Reference Name column** | Optional — a descriptive name included in results |
| **Query ID column** | The column of IDs you want to look up |

---

### Match Strategies

You can enable or disable each strategy independently. All three on gives the highest match rate.

| Strategy | What it does | Score |
|----------|-------------|-------|
| **Exact** | Matches after normalising case and whitespace | 100 |
| **Substring** | Matches if one ID appears inside the other (min 3 chars) | 100 |
| **Fuzzy** | Tolerates typos and formatting differences | Numeric (0–100) |

Strategies run in order — the first match wins. A query ID is only passed to Fuzzy if Exact and
Substring both failed.

---

### Advanced Settings

**Fuzzy Score Threshold** (default: 80)
The minimum similarity score required for a fuzzy match. Range 0–100.
- Lower → more lenient (higher match rate, risk of false positives)
- Higher → stricter (fewer false positives, may miss valid matches)
- Recommended starting range: 75–85

**Strip special characters** (default: on)
Treats `-`, `_`, and spaces as equivalent before exact comparison.
`SAMPLE-001` = `SAMPLE_001` = `SAMPLE 001`

**Normalize numeric padding** (default: off)
Strips leading zeros from numeric segments.
`S-1` = `S-01` = `S-001`
        """)

    # ------------------------------------------------------------------ Deduplication
    with st.expander("Deduplication"):
        st.markdown("""
Found in **Advanced Settings** (Wizard) or the **DEDUPLICATION** sidebar section (Expert).
Off by default — enable only when your files genuinely contain duplicate rows.

### What it does

Removes rows with duplicate values in the chosen key column before matching begins.
The summary stats show how many rows were removed.

### Options

| Option | Description |
|--------|-------------|
| **Deduplicate reference** | Remove duplicate rows from the reference database |
| **Deduplicate query** | Remove duplicate rows from the query sheet |
| **Key column** | Which column to check for duplicates (defaults to the selected ID column) |
| **Keep** | `First` — keep the first occurrence · `Last` — keep the last occurrence |

### When to use it

- Your reference database was assembled from multiple files and contains repeated entries
- Your query sheet has re-draw events or duplicate submissions you want to count once
- You want the summary "total query samples" to reflect unique IDs only

### When NOT to use it

- Duplicates in the query are meaningful (e.g., same sample at two time points)
- Your reference has multiple rows per sample with different metadata you need to preserve
        """)

    # ------------------------------------------------------------------ Manual Mappings
    with st.expander("Manual ID Mappings"):
        st.markdown("""
Found in **Advanced Settings** (Wizard) or the **MANUAL MAPPINGS** sidebar section (Expert).

### Purpose

Force-match specific Query IDs to Reference IDs that the automated matcher cannot resolve —
for example, when the IDs use completely different naming conventions with no lexical overlap.

Manual mappings are applied **before** any automated matching and always take priority.
They are recorded with strategy `"manual"` and score `100`.

### How to use it

1. **Run matching once** to find unmatched IDs.
2. Click **Pre-fill unmatched** to load all unmatched query IDs into the table.
3. For each row, select the correct Reference ID from the dropdown.
4. Optionally add a note explaining why this mapping was needed.
5. **Re-run matching** — your mappings will be applied automatically.

### Notes

- Only rows with both a Query ID and a Reference ID are applied — incomplete rows are ignored.
- The Reference ID dropdown is populated from your loaded reference database.
- Mappings persist across re-runs until you click **Clear all**.
- The "Pre-fill unmatched" button shows a count of currently unmatched IDs.
        """)

    # ------------------------------------------------------------------ Strategies deep dive
    with st.expander("Match Strategy Examples"):
        st.markdown("""
### Exact Match

```
Query:     SAMPLE_001
Reference: sample_001   ✓  (case difference)

Query:     SAMPLE  001
Reference: SAMPLE_001   ✓  (extra whitespace)
```

### Normalized Exact (Strip special characters enabled)

```
Query:     SAMPLE-001
Reference: SAMPLE_001   ✓  (dash vs underscore)

Query:     SAMPLE 001
Reference: SAMPLE_001   ✓  (space vs underscore)

Query:     ÁLPHA-015
Reference: ALPHA-015    ✓  (accented character → ASCII)
```

### Padding Normalization (enabled separately)

```
Query:     GNM-2024-5
Reference: GNM-2024-005  ✓  (leading zeros stripped)

Query:     S-01
Reference: S-1           ✓
```

### Substring Match

```
Query:     S001
Reference: LAB_S001_BATCH42   ✓  (query inside reference)

Query:     LAB_S001_BATCH42
Reference: S001               ✓  (reference inside query)
```

*Requires at least 3 characters in the normalized query ID to avoid spurious short-string matches.*

### Fuzzy Match

```
Query:     SAMPL_001        ← missing letter
Reference: SAMPLE_001       ✓  score ~93

Query:     SMAPLE_001       ← transposed letters
Reference: SAMPLE_001       ✓  score ~88

Query:     Smith John
Reference: John Smith       ✓  score ~100  (word-order handled)

Query:     PT-ALP-015       ← abbreviated cohort
Reference: PT-ALPHA-015     ✓  score ~91

Query:     GNM_2024_504     ← transposed digits
Reference: GNM-2024-054     ✗  score ~72 (below 80 threshold)
```

### Unmatched reasons

| Reason | Meaning |
|--------|---------|
| `empty_id` | Query ID is blank, "nan", or "none" |
| `no_candidates` | Reference database is empty |
| `below_threshold` | Best fuzzy score was below the threshold — check "Best Candidate" column |
        """)

    # ------------------------------------------------------------------ Results
    with st.expander("Reading Your Results"):
        st.markdown("""
### Summary Cards

At the top of the Results page:

| Card | Meaning |
|------|---------|
| **Total** | Number of rows in the query sheet |
| **Matched** | Successfully matched to a reference ID |
| **Unmatched** | Could not be matched |
| **Match Rate** | Matched ÷ Total × 100 |

The **Match Strategy Breakdown** expander shows how many matches came from each strategy.
If a large proportion came from Fuzzy, consider reviewing those rows carefully.

---

### Matched Samples Tab

Every query ID that was found in the reference. Columns:

| Column | Description |
|--------|-------------|
| Query ID | The original ID from your query sheet |
| Matched ID | The reference ID it was matched to |
| Sample Name | Name from the reference (if a name column was selected) |
| Strategy | Which strategy produced the match |
| Score | Similarity score (fuzzy only) |
| Extra columns | Any additional columns from the reference database |

**Filtering**: use the search box to filter by Query ID, Matched ID, or Sample Name.
Use the Strategy dropdown to show only matches from a specific strategy.

---

### Unmatched Tab

Every query ID that could not be matched. Columns:

| Column | Description |
|--------|-------------|
| Query ID | The original ID |
| Reason | `empty_id`, `below_threshold`, or `no_candidates` |
| Best Candidate | The closest reference ID found (even if below threshold) |

**What to do:**
1. Check `below_threshold` rows — the Best Candidate column shows what the matcher nearly matched.
   If correct, lower the fuzzy threshold or add a manual mapping.
2. Check for obvious typos in the Query ID.
3. Verify the sample actually exists in the reference database.
4. Use **Pre-fill unmatched** in Manual Mappings to batch-handle any remaining cases.
        """)

    # ------------------------------------------------------------------ Score colours
    with st.expander("Score Colour Coding"):
        st.markdown("""
The **Score** column uses colours both on-screen and in the Excel export.

| Colour | Score Range | Meaning |
|--------|-------------|---------|
| 🟢 **Green** | ≥ 90 | High-confidence fuzzy match — almost certainly correct |
| 🟡 **Amber** | 70 – 89 | Plausible match — a quick visual check is recommended |
| 🔴 **Red** | < 70 | Low-confidence — review carefully before accepting |
| **Grey italic** | — | Exact or Substring match — deterministic, no score needed |

**Tip:** If you see many Amber or Red matches, try:
- Raising the fuzzy threshold (e.g., 80 → 90) to avoid uncertain matches
- Checking that both files use the same ID scheme
- Enabling "Strip special characters" and/or "Normalize numeric padding"
        """)

    # ------------------------------------------------------------------ Download
    with st.expander("Downloading Your Results"):
        st.markdown("""
Click **⬇ Download (.xlsx)** at the bottom of the Results page (or in the Expert sidebar).

### Naming your file

A suggested filename is pre-filled based on the current date, time, and a short random suffix
(e.g., `results_20260311_142305_kxqr.xlsx`). Edit the text box to rename it before downloading.
If you forget the `.xlsx` extension it is added automatically.

### Excel workbook structure

| Sheet | Contents |
|-------|----------|
| **Summary** | Timestamp, totals, match rate, strategy breakdown, duplicate counts |
| **Matched** | All matched rows with ID, name, strategy, score, and extra reference columns |
| **Unmatched** | All unmatched rows with reason and best candidate |
| **All Results** | Complete combined view — useful for auditing or importing into LIMS |

All sheets include:
- Bold colour-coded headers
- Borders on every cell
- Automatic column widths
- Score-based colour highlighting (green / amber / red) on the Score column
        """)

    # ------------------------------------------------------------------ FAQ
    with st.expander("Troubleshooting & FAQ"):
        st.markdown("""
**The app detected the wrong ID column.**
→ In Step 2 (or the COLUMNS sidebar section in Expert mode), manually select the correct column
from the dropdown. The auto-detection is a starting point, not a requirement.

---

**My match rate is very low (< 50%).**
→ First check that you selected the correct ID columns — this is the most common cause.
→ Enable all three strategies (Exact, Substring, Fuzzy).
→ Enable "Strip special characters".
→ Lower the fuzzy threshold (try 70).
→ Verify both files are from the same project — mismatched datasets cannot be corrected by the matcher.

---

**I get an error when uploading my file.**
→ Ensure the file is `.xlsx`, `.xls`, or `.csv` — other formats are not supported.
→ Try re-saving from Excel (File → Save As).
→ Check the file is not password-protected or currently open in another program.

---

**Some IDs matched incorrectly (false positives).**
→ Raise the fuzzy threshold (e.g., 80 → 90) to demand higher similarity before accepting a match.
→ If short IDs are causing spurious substring matches, disable the Substring strategy.
→ Use Manual Mappings to pin the correct target for any known problematic IDs.

---

**Some IDs definitely exist in the reference but still show as unmatched.**
→ Check the "Best Candidate" column — it shows what the matcher almost matched.
→ If the candidate looks right, lower the fuzzy threshold or add a manual mapping.
→ Enable "Normalize numeric padding" if the difference is leading zeros.
→ Enable "Strip special characters" if separators differ.

---

**Can I load multiple reference files at once?**
→ Yes. Use the "Folder path" option to load all files from a directory — they are concatenated
into a single reference database automatically. All files must share the same column structure.

---

**Can I re-run with different settings without re-uploading?**
→ Yes. In Wizard mode, use the re-run panel in the sidebar (visible on Step 3).
  In Expert mode, adjust any setting and click **⟳ Re-run** — data is preserved.

---

**My manual mappings disappeared after a refresh.**
→ Streamlit resets all state on page refresh — this is normal browser behaviour.
  Re-upload your files and re-enter any manual mappings. For repeated use cases, consider keeping
  a CSV of your manual mappings so you can paste them back quickly.

---

**The "Pre-fill unmatched" button is greyed out.**
→ It activates only after you have run matching at least once and there are unmatched IDs.
  Run matching first, then use the button to populate the manual mappings table.

---

**How do I reset and start fresh?**
→ Click **↺ Start Over** at the bottom of the sidebar. This clears all loaded data, results,
  settings, and manual mappings.
        """)

    # ------------------------------------------------------------------ Tips
    with st.expander("Tips & Best Practices"):
        st.markdown("""
**Start with the defaults.** Exact + Substring + Fuzzy at threshold 80 with "Strip special
characters" on resolves the vast majority of real-world formatting differences without configuration.

**Run once before adding manual mappings.** The "Pre-fill unmatched" button saves you from typing
IDs manually — it loads all unmatched query IDs into the editor automatically.

**Use the Strategy Breakdown.** If a large share of matches came from Fuzzy at low scores, that's
a signal to review those rows. Consider raising the threshold and using manual mappings for the
remaining difficult cases.

**Use Expert Mode for iteration.** When you're adjusting the threshold or toggling strategies
repeatedly, Expert Mode lets you change settings and re-run without navigating between pages.

**Check the "Best Candidate" column for unmatched IDs.** Even when a match fails, the closest
reference ID is recorded. If it looks correct, the threshold was just slightly too high — lower it
or add a manual mapping for that specific pair.

**Keep the reference database clean.** Enable deduplication if your reference was assembled from
multiple sources and may contain repeated IDs. Use "Keep: last" if newer entries should win.

**Name your downloads meaningfully.** The suggested filename includes a timestamp and random suffix
for traceability. You can rename it (e.g., `plate_run_042_results.xlsx`) before downloading.

**Try the example datasets.** They are designed to demonstrate every strategy and edge case.
The "Genomics Run" dataset is a good first test — it covers all five matching strategies.
        """)
