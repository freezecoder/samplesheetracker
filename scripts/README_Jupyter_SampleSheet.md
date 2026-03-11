# Using the Extractor in Jupyter

This guide explains how to set up and run `extractor_notebook.ipynb` in Jupyter.

---

## Prerequisites

- Python 3.8+
- pip

---

## 1. Install Jupyter

If you don't have Jupyter installed:

```bash
pip install notebook
```

Or for JupyterLab:

```bash
pip install jupyterlab
```

---

## 2. Install required packages

```bash
pip install openpyxl pandas tabulate openpyxl
```

> `tabulate` is only needed if you use `DISPLAY_FORMAT = "markdown"`.

---

## 3. Open the notebook

Make sure `extractor_notebook.ipynb` and `extractor.py` are in the same directory, then launch Jupyter from that directory:

```bash
cd path/to/samplesheetracker/scripts
jupyter notebook
# or
jupyter lab
```

Open `extractor_notebook.ipynb` from the file browser.

---

## 4. Configure and run

Edit the **Config** cell — it mirrors every CLI option:

| Variable | CLI equivalent | Description |
|---|---|---|
| `FILE` | `file` (positional) | Path to your `.xlsm` / `.xlsx` workbook |
| `E1_SHEET` | `--e1-sheet` | Exact E1 sheet name (`None` = auto-detect) |
| `MANIFEST_SHEET` | `--manifest-sheet` | Exact Manifest sheet name (`None` = auto-detect) |
| `TABLE_LABEL` | `--table-label` | Substring to locate the table (default `"E.1. Table 5"`) |
| `NO_HEADER` | `--no-header` | `True` = first row is data, not headers |
| `SHOW` | `--show` | `"e1"` / `"manifest"` / `"both"` |
| `DISPLAY_FORMAT` | `--format` (preview) | `"table"` / `"csv"` / `"tsv"` / `"json"` / `"markdown"` |
| `MAX_ROWS` | `--max-rows` | Limit preview rows (`None` = all) |
| `EXPORT_FORMAT` | `--format` (export) | Same as above plus `"excel"` |
| `OUT_DIR` | `--out-dir` | Directory to save output files |
| `OUT_FILE` | `--out-file` | Exact output file path |

Then run all cells: **Kernel → Restart & Run All** (or `Shift+Enter` through each cell).

---

## 5. Export examples

### Export both tables to a single Excel workbook

```python
EXPORT_FORMAT = "excel"
OUT_DIR       = "./output"   # saves to ./output/output.xlsx
```

### Export to a specific file

```python
EXPORT_FORMAT = "excel"
OUT_FILE      = "./results.xlsx"
```

### Export each table as a CSV

```python
EXPORT_FORMAT = "csv"
OUT_DIR       = "./output"   # saves e1_table5.csv and manifest.csv
```

### Preview only (no export)

Leave both `OUT_DIR` and `OUT_FILE` as `None` — the Export cell will skip saving and print a message instead.

---

## 6. Listing sheet names

To inspect what sheets are in your workbook before running the full extraction, add a temporary cell:

```python
import openpyxl
wb = openpyxl.load_workbook("report.xlsm", read_only=True, keep_vba=False)
print(wb.sheetnames)
```
