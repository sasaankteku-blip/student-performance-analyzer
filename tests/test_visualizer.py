"""Tests for visualizer module and fractional threshold formatting."""

from pathlib import Path
import pytest
from student_performance_analyzer.analyzer import evaluate_course_performance
from student_performance_analyzer.validator import validate_and_assign_keys
from student_performance_analyzer.visualizer import (
    plot_grade_distributions,
    plot_pass_rates,
    plot_studytime_performance,
    plot_evaluation_period_progression,
)


def test_visualizer_fractional_threshold_labels(sample_dataframe, tmp_path):
    """Verify that visualizer charts generate without errors for a fractional threshold (e.g. 8.5)."""
    val_mat, _ = validate_and_assign_keys(sample_dataframe, "Mathematics", prefix="MAT")
    val_por, _ = validate_and_assign_keys(sample_dataframe, "Portuguese", prefix="POR")

    fractional_thresh = 8.5
    eval_mat, math_analysis = evaluate_course_performance(val_mat, "Mathematics", threshold=fractional_thresh)
    eval_por, por_analysis = evaluate_course_performance(val_por, "Portuguese", threshold=fractional_thresh)

    figures_dir = tmp_path / "figures"
    fig1 = plot_grade_distributions(eval_mat, eval_por, fractional_thresh, figures_dir / "grade_dist.png")
    fig2 = plot_pass_rates(math_analysis, por_analysis, figures_dir / "pass_rates.png")
    fig3 = plot_studytime_performance(math_analysis, por_analysis, figures_dir / "studytime.png")
    fig4 = plot_evaluation_period_progression(math_analysis, por_analysis, figures_dir / "period_prog.png")

    assert fig1.is_file() and fig1.stat().st_size > 0
    assert fig2.is_file() and fig2.stat().st_size > 0
    assert fig3.is_file() and fig3.stat().st_size > 0
    assert fig4.is_file() and fig4.stat().st_size > 0
