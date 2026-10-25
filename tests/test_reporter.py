"""Tests for markdown report generator."""

from pathlib import Path
from student_performance_analyzer.analyzer import evaluate_course_performance, compare_cohorts
from student_performance_analyzer.cleaner import audit_and_clean_records
from student_performance_analyzer.reporter import generate_markdown_report
from student_performance_analyzer.validator import validate_and_assign_keys


def test_markdown_report_content(sample_dataframe, tmp_path):
    """Verify required attribution, dynamic threshold text, no LaTeX backslashes, and no student-level PII."""
    val_mat, _ = validate_and_assign_keys(sample_dataframe, "Mathematics", prefix="MAT")
    val_por, _ = validate_and_assign_keys(sample_dataframe, "Portuguese", prefix="POR")

    clean_mat, audit_mat = audit_and_clean_records(val_mat, "Mathematics")
    clean_por, audit_por = audit_and_clean_records(val_por, "Portuguese")

    _, math_analysis = evaluate_course_performance(clean_mat, "Mathematics", threshold=8.0)
    _, por_analysis = evaluate_course_performance(clean_por, "Portuguese", threshold=8.0)
    comp = compare_cohorts(math_analysis, por_analysis)

    report_path = tmp_path / "test_report.md"
    generate_markdown_report(
        math_analysis=math_analysis,
        por_analysis=por_analysis,
        math_audit=audit_mat,
        por_audit=audit_por,
        comparison=comp,
        math_sha="fake_math_sha",
        por_sha="fake_por_sha",
        figure_paths=[],
        output_path=report_path,
    )

    assert report_path.is_file()
    content = report_path.read_text(encoding="utf-8")

    # Required attributions and citations
    assert "10.24432/C5TG7T" in content
    assert "CC BY 4.0" in content
    assert "Cortez" in content
    assert "Silva" in content

    # Plain text threshold without LaTeX math backslashes
    assert "G3 >= 8.0 / 20" in content or "G3 >= 8.0" in content
    assert "$G3" not in content
    assert "\\ge" not in content

    # Dynamic percentage: 8 / 20 is 40.0%
    assert "40.0%" in content
    assert "does not represent an official school policy" in content

    # Separation notes
    assert "strictly forbids record-level merging" in content

    # Verify NO student-level surrogate key leakage
    assert "MAT_0001" not in content
    assert "POR_0001" not in content


def test_markdown_report_custom_threshold(sample_dataframe, tmp_path):
    """Verify report dynamically reflects a custom threshold (e.g. 10.0 / 20 = 50.0%)."""
    val_mat, _ = validate_and_assign_keys(sample_dataframe, "Mathematics", prefix="MAT")
    val_por, _ = validate_and_assign_keys(sample_dataframe, "Portuguese", prefix="POR")

    clean_mat, audit_mat = audit_and_clean_records(val_mat, "Mathematics")
    clean_por, audit_por = audit_and_clean_records(val_por, "Portuguese")

    custom_thresh = 10.0
    _, math_analysis = evaluate_course_performance(clean_mat, "Mathematics", threshold=custom_thresh)
    _, por_analysis = evaluate_course_performance(clean_por, "Portuguese", threshold=custom_thresh)
    comp = compare_cohorts(math_analysis, por_analysis)

    report_path = tmp_path / "custom_thresh_report.md"
    generate_markdown_report(
        math_analysis=math_analysis,
        por_analysis=por_analysis,
        math_audit=audit_mat,
        por_audit=audit_por,
        comparison=comp,
        math_sha="sha_m",
        por_sha="sha_p",
        figure_paths=[],
        output_path=report_path,
    )

    content = report_path.read_text(encoding="utf-8")
    assert "10.0 / 20" in content
    assert "50.0%" in content
    assert "$G3" not in content


def test_markdown_report_displays_validation_invalids(sample_dataframe, tmp_path):
    """Verify that reports display invalid grade and studytime counts from ValidationReport."""
    from student_performance_analyzer.validator import ValidationReport

    val_mat, _ = validate_and_assign_keys(sample_dataframe, "Mathematics", prefix="MAT")
    val_por, _ = validate_and_assign_keys(sample_dataframe, "Portuguese", prefix="POR")

    clean_mat, audit_mat = audit_and_clean_records(val_mat, "Mathematics")
    clean_por, audit_por = audit_and_clean_records(val_por, "Portuguese")

    _, math_analysis = evaluate_course_performance(clean_mat, "Mathematics", threshold=8.0)
    _, por_analysis = evaluate_course_performance(clean_por, "Portuguese", threshold=8.0)
    comp = compare_cohorts(math_analysis, por_analysis)

    # Synthetic validation report with non-zero invalid counts
    synth_mat_val = ValidationReport(
        course_name="Mathematics",
        total_records=5,
        out_of_range_g1=2,
        out_of_range_g2=1,
        out_of_range_g3=3,
        invalid_studytime=4,
        ungradable_records=3,
        gradable_records=2,
    )
    synth_por_val = ValidationReport(
        course_name="Portuguese",
        total_records=5,
        out_of_range_g1=0,
        out_of_range_g2=0,
        out_of_range_g3=0,
        invalid_studytime=0,
        ungradable_records=0,
        gradable_records=5,
    )

    report_path = tmp_path / "invalids_report.md"
    generate_markdown_report(
        math_analysis=math_analysis,
        por_analysis=por_analysis,
        math_audit=audit_mat,
        por_audit=audit_por,
        comparison=comp,
        math_sha="sha_m",
        por_sha="sha_p",
        figure_paths=[],
        output_path=report_path,
        math_val_rep=synth_mat_val,
        por_val_rep=synth_por_val,
    )

    content = report_path.read_text(encoding="utf-8")
    assert "Invalid Grades (G1/G2/G3)" in content
    assert "Invalid Studytime" in content
    # Check that synthetic counts 2 / 1 / 3 and 4 appear
    assert "2 / 1 / 3" in content
    assert "Out-of-range G1=2, G2=1, G3=3; Invalid studytime=4" in content
