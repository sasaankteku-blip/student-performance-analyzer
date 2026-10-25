"""Tests for statistical analysis and pass/fail evaluation."""

import pytest
import numpy as np
import pandas as pd
from student_performance_analyzer.analyzer import (
    evaluate_course_performance,
    compare_cohorts,
    calculate_grade_stats,
)
from student_performance_analyzer.validator import validate_and_assign_keys


def test_pass_threshold_boundary(sample_dataframe):
    """CRITICAL TEST: Pass rule is G3 >= 8/20.

    - G3 = 7 must fail
    - G3 = 8 must pass
    - G1/G2 must NOT be averaged.
    """
    val_df, _ = validate_and_assign_keys(sample_dataframe, "Mathematics", prefix="MAT")
    eval_df, analysis = evaluate_course_performance(val_df, "Mathematics", threshold=8.0)

    # Row 0: G3=12 -> pass
    # Row 1: G3=8  -> pass (boundary)
    # Row 2: G3=7  -> fail (boundary)
    # Row 3: G3=0  -> fail
    # Row 4: G3=20 -> pass
    assert eval_df.loc[0, "passed"] == True
    assert eval_df.loc[1, "passed"] == True
    assert eval_df.loc[2, "passed"] == False
    assert eval_df.loc[3, "passed"] == False
    assert eval_df.loc[4, "passed"] == True

    assert analysis.pass_count == 3
    assert analysis.fail_count == 2
    assert analysis.pass_rate == pytest.approx(60.0)


def test_no_g1_g2_averaging(sample_dataframe):
    """Verify that high G1 and G2 scores do NOT rescue a student with G3=7."""
    df = sample_dataframe.copy()
    # Give student very high G1 and G2 (mean would be (20+20+7)/3 = 15.67 >= 8)
    df.loc[2, "G1"] = 20
    df.loc[2, "G2"] = 20
    df.loc[2, "G3"] = 7

    val_df, _ = validate_and_assign_keys(df, "Mathematics", prefix="MAT")
    eval_df, _ = evaluate_course_performance(val_df, "Mathematics", threshold=8.0)

    # Must FAIL because G3=7 is below 8
    assert eval_df.loc[2, "passed"] == False


def test_studytime_treated_as_ordinal(sample_dataframe):
    """Verify studytime is grouped by category labels 1, 2, 3, 4."""
    val_df, _ = validate_and_assign_keys(sample_dataframe, "Portuguese", prefix="POR")
    _, analysis = evaluate_course_performance(val_df, "Portuguese", threshold=8.0)

    assert len(analysis.studytime_stats) == 4
    categories = [st.category for st in analysis.studytime_stats]
    assert categories == [1, 2, 3, 4]


def test_course_separation_and_aggregate_comparison(sample_dataframe):
    """Verify Mathematics and Portuguese cohorts are analyzed separately

    and compared strictly at the aggregate level.
    """
    val_mat, _ = validate_and_assign_keys(sample_dataframe, "Mathematics", prefix="MAT")
    val_por, _ = validate_and_assign_keys(sample_dataframe, "Portuguese", prefix="POR")

    _, math_analysis = evaluate_course_performance(val_mat, "Mathematics", threshold=8.0)
    _, por_analysis = evaluate_course_performance(val_por, "Portuguese", threshold=8.0)

    comparison = compare_cohorts(math_analysis, por_analysis)
    assert comparison.math_records == 5
    assert comparison.por_records == 5
    assert any("strictly aggregate" in note for note in comparison.comparison_notes)


def test_evaluate_course_performance_without_is_gradable_column(sample_dataframe):
    """Verify that evaluate_course_performance functions correctly even if

    is_gradable column is missing (fallback creates row-aligned boolean mask).
    """
    raw_df = sample_dataframe.copy()
    assert "is_gradable" not in raw_df.columns

    eval_df, analysis = evaluate_course_performance(raw_df, "Mathematics", threshold=8.0)
    assert "is_gradable" in eval_df.columns
    assert "passed" in eval_df.columns
    assert analysis.gradable_records == 5
    assert analysis.pass_count == 3


def test_calculate_grade_stats_filters_invalid_scores():
    """Verify calculate_grade_stats excludes NaN and out-of-range (<0 or >20) grades."""
    series_with_invalids = pd.Series([10, 12, -5, 25, np.nan, "invalid", 14])
    stats = calculate_grade_stats(series_with_invalids)

    # Only 10, 12, 14 should be counted
    assert stats.count == 3
    assert stats.min_val == 10.0
    assert stats.max_val == 14.0
    assert stats.mean == pytest.approx(12.0)
    assert stats.median == 12.0


def test_evaluate_course_performance_invalid_threshold(sample_dataframe):
    """Verify ValueError is raised on non-numeric, out-of-bounds, or NaN/Inf thresholds."""
    val_df, _ = validate_and_assign_keys(sample_dataframe, "Mathematics", prefix="MAT")

    for bad_threshold in [-1.0, 20.5, float("nan"), float("inf"), "8.0"]:
        with pytest.raises(ValueError, match="Invalid pass threshold"):
            evaluate_course_performance(val_df, "Mathematics", threshold=bad_threshold)
