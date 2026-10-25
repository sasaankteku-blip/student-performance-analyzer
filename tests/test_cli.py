"""Tests for CLI error handling and execution."""

import math
from pathlib import Path
from student_performance_analyzer.cli import run_pipeline


def test_cli_missing_dataset_files(tmp_path):
    """Verify that CLI returns non-zero when dataset files are missing."""
    empty_data_dir = tmp_path / "empty_data"
    empty_data_dir.mkdir()
    reports_dir = tmp_path / "reports"
    figures_dir = tmp_path / "figures"

    exit_code = run_pipeline(
        data_dir=empty_data_dir,
        reports_dir=reports_dir,
        figures_dir=figures_dir,
        threshold=8.0,
    )
    assert exit_code == 1


def test_cli_invalid_threshold_values(tmp_path):
    """Verify that CLI returns 1 on invalid thresholds (negative, >20, NaN, inf)."""
    data_dir = Path("data/raw")
    reports_dir = tmp_path / "reports"
    figures_dir = tmp_path / "figures"

    for invalid_val in [-1.0, 20.1, 25.0, float("nan"), float("inf"), float("-inf")]:
        exit_code = run_pipeline(
            data_dir=data_dir,
            reports_dir=reports_dir,
            figures_dir=figures_dir,
            threshold=invalid_val,
        )
        assert exit_code == 1, f"Expected threshold {invalid_val} to be rejected"


def test_cli_successful_run(tmp_path):
    """Verify successful end-to-end execution of run_pipeline with real data."""
    data_dir = Path("data/raw")
    if not (data_dir / "student-mat.csv").exists():
        return

    reports_dir = tmp_path / "reports"
    figures_dir = tmp_path / "reports" / "figures"

    exit_code = run_pipeline(
        data_dir=data_dir,
        reports_dir=reports_dir,
        figures_dir=figures_dir,
        threshold=8.0,
    )
    assert exit_code == 0
    assert (reports_dir / "analysis_report.md").is_file()
    assert (figures_dir / "grade_distributions.png").is_file()
    assert (figures_dir / "pass_rates_comparison.png").is_file()
    assert (figures_dir / "studytime_performance.png").is_file()
    assert (figures_dir / "period_grade_progression.png").is_file()
