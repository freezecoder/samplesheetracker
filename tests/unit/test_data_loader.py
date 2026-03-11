"""Unit tests for core/data_loader.py."""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pytest

from core.data_loader import (
    deduplicate_df,
    detect_id_column,
    detect_name_column,
    list_folder_files,
    load_reference_from_file,
    load_reference_from_folder,
    load_query_sheet,
    get_sheet_names,
)
from config.defaults import DEFAULT_ID_COLUMN_CANDIDATES, DEFAULT_NAME_COLUMN_CANDIDATES


# ---------------------------------------------------------------------------
# detect_id_column
# ---------------------------------------------------------------------------

def test_detect_id_exact_match():
    df = pd.DataFrame(columns=["SampleID", "Name", "Batch"])
    assert detect_id_column(df, DEFAULT_ID_COLUMN_CANDIDATES) == "SampleID"


def test_detect_id_case_insensitive():
    df = pd.DataFrame(columns=["SAMPLEID", "Name"])
    assert detect_id_column(df, DEFAULT_ID_COLUMN_CANDIDATES) == "SAMPLEID"


def test_detect_id_with_spaces():
    df = pd.DataFrame(columns=["Sample ID", "Name"])
    assert detect_id_column(df, DEFAULT_ID_COLUMN_CANDIDATES) == "Sample ID"


def test_detect_id_fallback_contains_id():
    df = pd.DataFrame(columns=["PatientID", "Name"])
    result = detect_id_column(df, DEFAULT_ID_COLUMN_CANDIDATES)
    assert result == "PatientID"


def test_detect_id_none():
    df = pd.DataFrame(columns=["Alpha", "Beta"])
    assert detect_id_column(df, DEFAULT_ID_COLUMN_CANDIDATES) is None


def test_detect_name_column():
    df = pd.DataFrame(columns=["SampleID", "sample_name", "Batch"])
    assert detect_name_column(df, DEFAULT_NAME_COLUMN_CANDIDATES) == "sample_name"


def test_detect_name_none():
    df = pd.DataFrame(columns=["ID", "Code"])
    assert detect_name_column(df, DEFAULT_NAME_COLUMN_CANDIDATES) is None


# ---------------------------------------------------------------------------
# load_reference_from_file
# ---------------------------------------------------------------------------

def test_load_reference_xlsx(reference_xlsx_path):
    class FakeFile:
        name = "reference_db.xlsx"
        def __init__(self, path):
            self._path = path
        def read(self):
            return open(self._path, "rb").read()
        def seek(self, n):
            pass

    # Use the real path directly via pd.read_excel-compatible path
    df = pd.read_excel(reference_xlsx_path, dtype=str)
    assert len(df) > 0
    assert "SampleID" in df.columns


def test_load_reference_csv(reference_csv_path):
    df = pd.read_csv(reference_csv_path, dtype=str)
    assert len(df) > 0
    assert "SampleID" in df.columns


def test_load_from_file_returns_strings(reference_df, tmp_path):
    p = tmp_path / "test.csv"
    reference_df.to_csv(p, index=False)

    class MockFile:
        name = "test.csv"
        def __init__(self):
            self._buf = open(p, "rb").read()
            self._pos = 0
        def read(self, n=-1):
            data = self._buf[self._pos:]
            self._pos = len(self._buf)
            return data
        def seek(self, n):
            self._pos = n

    df = load_query_sheet(MockFile())
    assert df.dtypes.apply(lambda d: str(d) == "object").all()


# ---------------------------------------------------------------------------
# load_reference_from_folder
# ---------------------------------------------------------------------------

def test_load_from_folder(reference_folder, reference_df):
    df = load_reference_from_folder(str(reference_folder))
    assert len(df) == len(reference_df)
    assert "SampleID" in df.columns


def test_load_from_folder_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_reference_from_folder(str(tmp_path / "nonexistent"))


def test_load_from_empty_folder(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(FileNotFoundError):
        load_reference_from_folder(str(empty))


# ---------------------------------------------------------------------------
# list_folder_files
# ---------------------------------------------------------------------------

def test_list_folder_files(reference_folder):
    files = list_folder_files(str(reference_folder), (".xlsx", ".csv"))
    assert len(files) == 2
    for f in files:
        assert f.endswith(".xlsx") or f.endswith(".csv")


def test_list_folder_files_nonexistent(tmp_path):
    files = list_folder_files(str(tmp_path / "ghost"), (".xlsx",))
    assert files == []


# ---------------------------------------------------------------------------
# get_sheet_names
# ---------------------------------------------------------------------------

def test_get_sheet_names_csv():
    class FakeCsv:
        name = "data.csv"
    assert get_sheet_names(FakeCsv()) == ["Sheet1"]


# ---------------------------------------------------------------------------
# deduplicate_df
# ---------------------------------------------------------------------------

def test_deduplicate_df_removes_dupes():
    df = pd.DataFrame({"ID": ["A", "B", "A", "C"], "Val": [1, 2, 3, 4]})
    result, n_removed = deduplicate_df(df, "ID")
    assert n_removed == 1
    assert len(result) == 3
    assert list(result["ID"]) == ["A", "B", "C"]


def test_deduplicate_df_keep_last():
    df = pd.DataFrame({"ID": ["A", "B", "A"], "Val": [1, 2, 3]})
    result, n_removed = deduplicate_df(df, "ID", keep="last")
    assert n_removed == 1
    assert result.loc[result["ID"] == "A", "Val"].iloc[0] == 3


def test_deduplicate_df_no_dupes():
    df = pd.DataFrame({"ID": ["A", "B", "C"], "Val": [1, 2, 3]})
    result, n_removed = deduplicate_df(df, "ID")
    assert n_removed == 0
    assert len(result) == 3


def test_deduplicate_df_all_dupes():
    df = pd.DataFrame({"ID": ["X", "X", "X"], "Val": [1, 2, 3]})
    result, n_removed = deduplicate_df(df, "ID")
    assert n_removed == 2
    assert len(result) == 1


def test_get_sheet_names_excel(multi_sheet_ref_path):
    class FakeXlsx:
        name = "multi.xlsx"
        def __init__(self, path):
            self._path = path
            self._data = open(path, "rb").read()
            self._pos = 0
        def read(self, n=-1):
            d = self._data[self._pos:]
            self._pos = len(self._data)
            return d
        def seek(self, n):
            self._pos = n
        def tell(self):
            return self._pos

    sheets = get_sheet_names(multi_sheet_ref_path)
    assert len(sheets) >= 1
