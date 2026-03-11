# xlsm extractor

Extracts two tables from an Excel macro-enabled workbook (`.xlsm` / `.xlsx`):

- **E.1. Table 5** — located by label inside the *E1 Norm+Pool* sheet
- **H.1 Manifest** — the full *Manifest* sheet

Works as a standalone CLI script or as an importable Python module.

---

## Requirements

```
pip install openpyxl pandas tabulate
```

> `tabulate` is only needed for `--format markdown`.
> Python 3.8+ required.

---

## Quick start

```bash
# Print both tables to the terminal
python extractor.py report.xlsm

# Inspect what sheets exist before extracting
python extractor.py report.xlsm --list-sheets

# Preview column names and row counts without printing all data
python extractor.py report.xlsm --info
```

---

## CLI reference

```
python extractor.py <file> [options]
```

### Positional

| Argument | Description |
|----------|-------------|
| `file` | Path to the `.xlsm` or `.xlsx` workbook |

### Sheet / table options

| Flag | Default | Description |
|------|---------|-------------|
| `--e1-sheet NAME` | auto | Exact sheet name for the E1 Norm+Pool sheet. Skips auto-detection. |
| `--manifest-sheet NAME` | auto | Exact sheet name for the Manifest sheet. Skips auto-detection. |
| `--table-label TEXT` | `E.1. Table 5` | Substring to search for when locating the target table in the E1 sheet. Case-insensitive. |
| `--no-header` | off | Treat the first data row as data rather than column names. |

### Output options

| Flag | Default | Description |
|------|---------|-------------|
| `--show TABLE` | `both` | Which table to print/export: `e1` \| `manifest` \| `both` |
| `--format FMT`, `-f FMT` | `table` | Output format: `table` \| `csv` \| `tsv` \| `json` \| `markdown` |
| `--max-rows N` | none | Limit output to the first N rows. Useful for previewing large tables. |
| `--out-dir DIR` | none | Write output files to this directory instead of printing to stdout. Files are named `e1_table5.<ext>` and `manifest.<ext>`. |
| `--out-file FILE` | none | Write a single table to this exact path. Only valid when `--show` is `e1` or `manifest`, not `both`. |

### Info commands

| Flag | Description |
|------|-------------|
| `--list-sheets` | Print all sheet names in the workbook and exit. No data is extracted. |
| `--info` | Print the shape (rows × columns) and column names for each extracted table, then exit. |

---

## Examples

```bash
# Print both tables in aligned-text format
python extractor.py report.xlsm

# List all sheet names in the workbook
python extractor.py report.xlsm --list-sheets

# Show column names and row counts without printing all data
python extractor.py report.xlsm --info

# Preview just the first 10 rows of the E1 table
python extractor.py report.xlsm --show e1 --max-rows 10

# Export both tables as CSV files into ./output/
python extractor.py report.xlsm --out-dir ./output --format csv
#   writes: output/e1_table5.csv
#           output/manifest.csv

# Export the manifest sheet as JSON to a specific file
python extractor.py report.xlsm --show manifest --out-file manifest.json --format json

# Print the E1 table as a Markdown table
python extractor.py report.xlsm --show e1 --format markdown

# Use custom sheet names (when auto-detection doesn't match)
python extractor.py report.xlsm \
    --e1-sheet "E1 Norm+Pool" \
    --manifest-sheet "H.1 Manifest"

# Search for a different table label
python extractor.py report.xlsm --table-label "Table 5"

# Treat the first row as data instead of headers
python extractor.py report.xlsm --no-header
```

---

## Python API

Import `extract()` to get both DataFrames directly in your code.

### Signature

```python
extract(
    filepath: str,
    *,
    e1_sheet: str | None = None,
    manifest_sheet: str | None = None,
    table_label: str = "E.1. Table 5",
    no_header: bool = False,
) -> list[pd.DataFrame]
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filepath` | `str` | — | Path to the `.xlsm` / `.xlsx` file |
| `e1_sheet` | `str \| None` | `None` | Exact sheet name for the E1 sheet. Auto-detected if omitted. |
| `manifest_sheet` | `str \| None` | `None` | Exact sheet name for the Manifest sheet. Auto-detected if omitted. |
| `table_label` | `str` | `"E.1. Table 5"` | Label text to search for inside the E1 sheet. Case-insensitive substring match. |
| `no_header` | `bool` | `False` | If `True`, the first data row is treated as data rather than column names. |

### Returns

A list of two `pandas.DataFrame` objects:

```
[0]  e1_df       – rows from the matched table in the E1 Norm+Pool sheet
[1]  manifest_df – all rows from the Manifest sheet
```

### Usage examples

```python
from extractor import extract

# Basic usage — returns [e1_df, manifest_df]
e1_df, manifest_df = extract("report.xlsm")

print(e1_df.head())
print(manifest_df.shape)
```

```python
# Override sheet names and table label
e1_df, manifest_df = extract(
    "report.xlsm",
    e1_sheet="E1 Norm+Pool",
    manifest_sheet="H.1 Manifest",
    table_label="Table 5",
)
```

```python
# No header row — columns will be 0-indexed integers
e1_df, manifest_df = extract("report.xlsm", no_header=True)
```

```python
# Work with the DataFrames normally
import pandas as pd

e1_df, manifest_df = extract("report.xlsm")

# Filter, export, merge, etc.
e1_df.to_csv("e1.csv", index=False)
manifest_df.to_excel("manifest.xlsx", index=False)
merged = e1_df.merge(manifest_df, on="SampleID")
```

---

## How table detection works

For the E1 sheet the script does not rely on a fixed cell address. Instead:

1. Scans every cell in the sheet for one containing `--table-label` (default `"E.1. Table 5"`) as a case-insensitive substring.
2. Treats the first non-empty row **below** the label as the column header row.
3. Detects the column span automatically from that header row (leftmost to rightmost non-empty cell).
4. Reads data rows downward until it hits a row that is fully empty across those columns.

This makes extraction resilient to blank rows above the table, extra content elsewhere on the sheet, and minor label formatting differences.

The Manifest sheet is read in full from row 1, with the first row used as column headers.

---

## Auto-detection rules

When `--e1-sheet` / `e1_sheet` is not provided, the script picks the first sheet whose name contains `"e1 norm"` (case-insensitive, spaces ignored).
When `--manifest-sheet` / `manifest_sheet` is not provided, it picks the first sheet whose name contains `"manifest"`.

If no match is found a `ValueError` is raised listing all available sheet names. Use `--list-sheets` to see them first.
