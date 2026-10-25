"""Tests for schema and record validator module."""

import pytest
import pandas as pd
from student_performance_analyzer.validator import (
    validate_schema,
    validate_and_assign_keys,
)


def test_validate_schema_complete(sample_dataframe):
    """Verify that a DataFrame with all 33 expected columns passes schema check."""
    missing, extra = validate_schema(sample_dataframe)
    assert len(missing) == 0
    assert len(extra) == 0


def test_validate_schema_missing_column(sample_dataframe):
    """Verify detection of missing required column."""
    df_missing = sample_dataframe.drop(columns=["G3"])
    missing, extra = validate_schema(df_missing)
    assert "G3" in missing


def test_surrogate_key_assignment(sample_dataframe):
    """Verify that surrogate keys are assigned per cohort without demographic merging."""
    validated, report = validate_and_assign_keys(sample_dataframe, "Mathematics", prefix="MAT")
    assert "surrogate_key" in validated.columns
    assert validated.iloc[0]["surrogate_key"] == "MAT_0001"
    assert validated.iloc[1]["surrogate_key"] == "MAT_0002"
    assert report.total_records == 5
    assert report.gradable_records == 5
    assert report.ungradable_records == 0


def test_grade_range_validation(sample_dataframe):
    """Verify that grades < 0 or > 20 are flagged as out-of-range and ungradable."""
    df_invalid = sample_dataframe.copy()
    # Add an out-of-range grade
    df_invalid.loc[0, "G3"] = 25  # > 20
    df_invalid.loc[1, "G3"] = -2  # < 0

    validated, report = validate_and_assign_keys(df_invalid, "Mathematics", prefix="MAT")
    assert report.out_of_range_g3 == 2
    assert report.ungradable_records == 2
    assert report.gradable_records == 3
    assert not validated.loc[0, "is_gradable"]
    assert not validated.loc[1, "is_gradable"]
