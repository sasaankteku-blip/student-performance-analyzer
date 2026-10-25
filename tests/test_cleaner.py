"""Tests for duplicate detection and row preservation."""

import pytest
import pandas as pd
from student_performance_analyzer.cleaner import audit_and_clean_records


def test_exact_duplicates_detected_and_preserved(sample_dataframe):
    """CRITICAL TEST: Exact duplicate rows must be counted and flagged,

    but NEVER silently dropped or deduplicated.
    """
    # Create duplicate by repeating row 0
    df_with_dups = pd.concat([sample_dataframe, sample_dataframe.iloc[[0]]], ignore_index=True)
    assert len(df_with_dups) == 6

    cleaned, report = audit_and_clean_records(df_with_dups, "Mathematics")

    # Duplicates audited
    assert report.total_records == 6
    assert report.exact_duplicates_count == 1
    assert report.records_retained == 6  # Preserved!
    assert len(cleaned) == 6             # Never silently deleted!
    assert "is_exact_duplicate" in cleaned.columns
    assert cleaned.iloc[5]["is_exact_duplicate"] == True
    assert cleaned.iloc[0]["is_exact_duplicate"] == False


def test_no_demographic_deduplication(sample_dataframe):
    """Verify rows sharing only demographic fields are NOT treated as exact duplicates."""
    df_demo = sample_dataframe.copy()
    # Make row 1 have same demographics as row 0, but different grades
    df_demo.loc[1, "G1"] = 15
    df_demo.loc[1, "G2"] = 16
    df_demo.loc[1, "G3"] = 17

    cleaned, report = audit_and_clean_records(df_demo, "Portuguese")
    assert report.exact_duplicates_count == 0
    assert len(cleaned) == 5
