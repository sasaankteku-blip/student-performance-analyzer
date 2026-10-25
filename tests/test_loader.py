"""Tests for CSV loader module."""

import pytest
from pathlib import Path
from student_performance_analyzer.loader import load_student_csv


def test_load_valid_semicolon_csv(tmp_path):
    """Verify loading of a standard semicolon-delimited CSV."""
    p = tmp_path / "valid.csv"
    p.write_text("school;sex;age\nGP;F;17\nMS;M;18\n", encoding="utf-8")

    df = load_student_csv(p, delimiter=";")
    assert len(df) == 2
    assert list(df.columns) == ["school", "sex", "age"]
    assert df.iloc[0]["school"] == "GP"


def test_load_file_not_found():
    """Verify FileNotFoundError when file does not exist."""
    with pytest.raises(FileNotFoundError):
        load_student_csv("/nonexistent/path/data.csv")


def test_load_empty_file(tmp_path):
    """Verify ValueError when attempting to load an empty file."""
    p = tmp_path / "empty.csv"
    p.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        load_student_csv(p)


def test_load_real_uci_data():
    """Integration check: verify loading real raw UCI files."""
    data_dir = Path("data/raw")
    mat_file = data_dir / "student-mat.csv"
    por_file = data_dir / "student-por.csv"

    if mat_file.exists():
        df_mat = load_student_csv(mat_file, delimiter=";")
        assert len(df_mat) == 395
        assert len(df_mat.columns) == 33

    if por_file.exists():
        df_por = load_student_csv(por_file, delimiter=";")
        assert len(df_por) == 649
        assert len(df_por.columns) == 33
