# Sample Sheet Tracker

A Streamlit web app for matching sample IDs from a query sheet against a reference database — even when the IDs are formatted differently.

Built for lab environments where sample identifiers vary across instruments, operators, and systems (extra dashes, missing zeros, typos, alternate separators, word-order differences, etc.).

---

## Features

- **Five-layer matching pipeline** — Exact → Normalized Exact → Padding Normalization → Substring → Fuzzy, running sequentially and stopping at the first match
- **Fuzzy matching** via `RapidFuzz` `token_set_ratio` — handles word order, typos, and abbreviations
- **Manual override table** — force-match specific IDs the automated matcher can't resolve
- **Deduplication** — optionally remove duplicate rows from either file before matching, on any key column
- **Wizard Mode** — 3-step guided workflow for new users
- **Expert Mode** — single-page sidebar-driven interface for rapid iteration
- **Formatted Excel export** — 4-sheet report (Summary, Matched, Unmatched, All Results) with score-based colour coding
- **3 themes** — Light, Beige, Dark
- **4 built-in example datasets** covering 18+ real-world ID formatting challenges
- **65 unit + integration tests** covering all edge cases

---

## Quick Start

### Requirements

- Python 3.10+
- Packages listed in `requirements.txt`

### Install

```bash
git clone <repo-url>
cd samplesheetracker
pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## Project Structure

```
samplesheetracker/
├── app.py                    # Entry point, tab router, session defaults
├── core/
│   ├── matcher.py            # Matching engine — MatchConfig, MatchResult, match_all
│   ├── data_loader.py        # File/folder loading, column detection, deduplication
│   ├── report_generator.py   # DataFrame builders, summary stats
│   └── excel_exporter.py     # 4-sheet xlsx export with xlsxwriter formatting
├── ui/
│   ├── sidebar.py            # Mode toggle, Wizard sidebar, Expert sidebar
│   ├── page_load.py          # Step 1 — Load Data
│   ├── page_configure.py     # Step 2 — Configure Matching
│   ├── page_results.py       # Step 3 — Results
│   ├── page_userguide.py     # User Guide tab
│   ├── matching_runner.py    # Shared run_matching() called by all entry points
│   ├── components.py         # Reusable widgets (badges, metric cards, callouts)
│   └── stepper.py            # Progress stepper for Wizard mode
├── config/
│   └── defaults.py           # ID/name column candidates, strategy labels, extensions
├── data/
│   └── example_datasets.py   # 4 built-in challenging datasets
├── themes/
│   └── __init__.py           # Light / Beige / Dark CSS injection
├── assets/
│   └── logo_placeholder.png
└── tests/
    ├── unit/
    │   ├── test_matcher.py
    │   ├── test_data_loader.py
    │   └── test_report_generator.py
    └── integration/
        └── test_end_to_end.py
```

---

## How Matching Works

Each query ID is passed through five strategies in order. The first match wins.

| # | Strategy | Trigger | What it does |
|---|----------|---------|-------------|
| 1 | **Exact** | Always | Lowercase + whitespace-normalize, then compare |
| 2 | **Normalized Exact** | `strip_special = True` | Also removes dashes, underscores, and non-ASCII characters |
| 3 | **Padding Normalization** | `normalize_padding = True` | Strips numeric leading zeros: `S-01 == S-1` |
| 4 | **Substring** | `use_substring = True` | Query appears inside reference ID, or vice versa (min 3 chars) |
| 5 | **Fuzzy** | `use_fuzzy = True` | `token_set_ratio` score ≥ `fuzzy_threshold` |

If no strategy matches, the query ID is recorded as unmatched with a reason:

| Reason | Meaning |
|--------|---------|
| `empty_id` | Query ID was blank, `nan`, or `none` |
| `no_candidates` | Reference database was empty |
| `below_threshold` | Best fuzzy score was below the threshold |

### Manual Mappings

Manual mappings are applied **before** automated matching and always win. Each mapping is: `Query ID → Reference ID (+ optional note)`. Strategy is recorded as `"manual"`, score as `100.0`.

---

## Configuration Reference

### MatchConfig fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `use_exact` | bool | `True` | Enable exact matching |
| `use_substring` | bool | `True` | Enable substring matching |
| `use_fuzzy` | bool | `True` | Enable fuzzy matching |
| `fuzzy_threshold` | int | `80` | Minimum score (0–100) for a fuzzy match |
| `strip_special` | bool | `True` | Strip `-`, `_`, spaces for normalized exact match |
| `normalize_padding` | bool | `False` | Treat `S-1` and `S-01` as equal |

### Deduplication options

| Option | Default | Description |
|--------|---------|-------------|
| `dedup_ref` | `False` | Remove duplicate rows from reference before matching |
| `dedup_query` | `False` | Remove duplicate rows from query before matching |
| `dedup_keep` | `"first"` | Which duplicate to retain (`"first"` or `"last"`) |
| `dedup_ref_key` | ref ID col | Column to deduplicate reference on |
| `dedup_query_key` | query ID col | Column to deduplicate query on |

---

## Modes

### Wizard Mode (default)

Guided 3-step flow:
1. **Load Data** — upload reference and query files
2. **Configure** — select columns, strategies, advanced settings, manual mappings
3. **Results** — view and download

Sidebar shows step progress and a re-run panel on Step 3.

### Expert Mode

Toggle in the sidebar (above the stepper). All controls collapse into sidebar sections:

- **DATA** — upload or load from folder
- **COLUMNS** — select ID and name columns
- **MATCH SETTINGS** — strategies, threshold, normalization
- **DEDUPLICATION** — per-file dedup with key column selection
- **MANUAL MAPPINGS** — force-match editor

Results appear immediately in the main panel. Click **⟳ Re-run** to iterate without leaving the page. No session state is reset when toggling modes.

---

## Excel Export

Every download contains four sheets:

| Sheet | Contents |
|-------|----------|
| **Summary** | Timestamp, totals, match rate, strategy breakdown, dupe counts |
| **Matched** | All matched rows — Query ID, Matched ID, Sample Name, Strategy, Score, extra ref columns |
| **Unmatched** | All unmatched rows — Query ID, Reason, Best Candidate |
| **All Results** | Full combined view for auditing |

Score colour coding (mirrors the on-screen table):

| Score | Background |
|-------|-----------|
| ≥ 90 | Green |
| 70 – 89 | Amber |
| < 70 | Red |
| Exact / Substring | Grey italic |

---

## Example Datasets

Four built-in datasets cover common real-world challenges. Load them from the **"Try with example data"** expander on Step 1.

| Dataset | Ref rows | Query rows | Key challenges |
|---------|----------|------------|---------------|
| Genomics Run — 96-Well Plate | 60 | 30 | Separator variants, missing zeros, Unicode hyphens, operator prefixes, control samples |
| Clinical Trial Specimens | 70 | 28 | Reversed word order, abbreviations, Unicode accents, slash separators, visit suffixes, duplicates |
| Biobank Short IDs | 100 | 30 | Short-ID collisions, O vs 0, leading zeros, aliquot suffixes, truncated IDs |
| Proteomics Multi-Site Study | 180 | 25 | Dot/slash separators, site code typos, timepoint word-order swaps, institution prefixes |

---

## Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest --cov=core --cov=ui --cov-report=term-missing

# Quick pass/fail
pytest tests/ -q
```

69 tests across unit and integration suites. All core matching edge cases from the spec are covered.

---

## Themes

Select from the sidebar dropdown:

- **Light** — default, blue accent on white
- **Beige** — warm off-white with brown accents
- **Dark** — navy background with cyan accents

---

## Session State Keys

| Key | Type | Description |
|-----|------|-------------|
| `current_step` | int | Active wizard step (1/2/3) |
| `app_mode` | str | `"Wizard"` or `"Expert"` |
| `theme` | str | `"Light"`, `"Beige"`, or `"Dark"` |
| `ref_df` | DataFrame | Loaded reference database |
| `query_df` | DataFrame | Loaded query sheet |
| `ref_id_col` | str | Selected reference ID column |
| `ref_name_col` | str \| None | Selected reference name column |
| `query_id_col` | str | Selected query ID column |
| `match_config` | MatchConfig | Last-used match configuration |
| `results_df` | DataFrame | All results (matched + unmatched) |
| `matched_df` | DataFrame | Matched rows only |
| `unmatched_df` | DataFrame | Unmatched rows only |
| `summary_stats` | dict | Match rate, counts, strategy breakdown, dupe counts |
| `manual_mappings_df` | DataFrame | Manual override table |
| `download_filename` | str | Suggested export filename |
