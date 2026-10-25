"""Command Line Interface for the Student Performance Analyzer."""

import argparse
import hashlib
import math
from pathlib import Path
import sys
from .analyzer import compare_cohorts, evaluate_course_performance
from .cleaner import audit_and_clean_records
from .constants import DEFAULT_PASS_THRESHOLD, MIN_GRADE, MAX_GRADE
from .loader import load_student_csv
from .reporter import generate_markdown_report
from .validator import validate_and_assign_keys
from .visualizer import (
    plot_evaluation_period_progression,
    plot_grade_distributions,
    plot_pass_rates,
    plot_studytime_performance,
)


def compute_sha256(filepath: Path) -> str:
    """Compute the SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def run_pipeline(
    data_dir: Path,
    reports_dir: Path,
    figures_dir: Path,
    threshold: float = DEFAULT_PASS_THRESHOLD,
) -> int:
    """Run the end-to-end Student Performance Analyzer pipeline."""
    # Validate threshold is finite and in range [0, 20]
    if not isinstance(threshold, (int, float)) or math.isnan(threshold) or math.isinf(threshold) or not (MIN_GRADE <= threshold <= MAX_GRADE):
        print(
            f"ERROR: Invalid pass threshold '{threshold}'. "
            f"Threshold must be a finite number between {MIN_GRADE}.0 and {MAX_GRADE}.0.",
            file=sys.stderr,
        )
        return 1

    pct = (threshold / MAX_GRADE) * 100.0

    print("=" * 70)
    print("  Student Performance Analyzer — End-to-End Pipeline")
    print("=" * 70)
    print(f"Data directory:      {data_dir}")
    print(f"Reports directory:   {reports_dir}")
    print(f"Figures directory:   {figures_dir}")
    print(f"Pass threshold:      {threshold:.1f} / 20 (Illustrative {pct:.1f}% benchmark)")
    print("-" * 70)

    if not data_dir.is_dir():
        print(f"ERROR: Dataset directory not found or not a directory: {data_dir}", file=sys.stderr)
        return 1

    math_path = data_dir / "student-mat.csv"
    por_path = data_dir / "student-por.csv"

    for path in [math_path, por_path]:
        if not path.is_file():
            print(f"ERROR: Expected dataset file not found: {path}", file=sys.stderr)
            print("Please verify that raw CSVs are extracted into the data directory.", file=sys.stderr)
            return 1

    # Compute checksums
    math_sha = compute_sha256(math_path)
    por_sha = compute_sha256(por_path)
    print(f"[OK] Ingested Mathematics dataset ({math_path.name})")
    print(f"     SHA-256: {math_sha}")
    print(f"[OK] Ingested Portuguese dataset  ({por_path.name})")
    print(f"     SHA-256: {por_sha}")
    print("-" * 70)

    # 1. Load CSV files
    try:
        math_raw = load_student_csv(math_path, delimiter=";")
        por_raw = load_student_csv(por_path, delimiter=";")
    except Exception as e:
        print(f"ERROR: Data loading failed: {e}", file=sys.stderr)
        return 1

    # 2. Validate Schema & Assign Surrogate Keys
    try:
        math_val, math_val_rep = validate_and_assign_keys(math_raw, "Mathematics", prefix="MAT")
        por_val, por_val_rep = validate_and_assign_keys(por_raw, "Portuguese", prefix="POR")
    except Exception as e:
        print(f"ERROR: Schema validation failed: {e}", file=sys.stderr)
        return 1

    print(f"[OK] Schema validated: Mathematics={len(math_val)} rows, Portuguese={len(por_val)} rows (all 33 columns present)")

    # 3. Clean & Audit (Duplicates & Missing Values)
    math_clean, math_audit = audit_and_clean_records(math_val, "Mathematics")
    por_clean, por_audit = audit_and_clean_records(por_val, "Portuguese")

    print(f"[OK] Duplicates audited: Mathematics has {math_audit.exact_duplicates_count} duplicates; Portuguese has {por_audit.exact_duplicates_count} duplicates")
    print("     (All rows preserved; zero rows silently deleted)")

    # 4. Statistical Analysis & Pass/Fail Evaluation
    math_eval, math_analysis = evaluate_course_performance(math_clean, "Mathematics", threshold=threshold)
    por_eval, por_analysis = evaluate_course_performance(por_clean, "Portuguese", threshold=threshold)
    comparison = compare_cohorts(math_analysis, por_analysis)

    print("-" * 70)
    print(f"Mathematics (N={math_analysis.total_records}): Pass Rate = {math_analysis.pass_rate:.1f}% ({math_analysis.pass_count} passed, {math_analysis.fail_count} failed)")
    print(f"             Mean G3 = {math_analysis.g3_stats.mean:.2f}, Median G3 = {math_analysis.g3_stats.median:.1f}")
    print(f"Portuguese  (N={por_analysis.total_records}): Pass Rate = {por_analysis.pass_rate:.1f}% ({por_analysis.pass_count} passed, {por_analysis.fail_count} failed)")
    print(f"             Mean G3 = {por_analysis.g3_stats.mean:.2f}, Median G3 = {por_analysis.g3_stats.median:.1f}")
    print("-" * 70)

    # 5. Generate Visualizations
    figures_dir.mkdir(parents=True, exist_ok=True)
    fig1 = plot_grade_distributions(math_eval, por_eval, threshold, figures_dir / "grade_distributions.png")
    fig2 = plot_pass_rates(math_analysis, por_analysis, figures_dir / "pass_rates_comparison.png")
    fig3 = plot_studytime_performance(math_analysis, por_analysis, figures_dir / "studytime_performance.png")
    fig4 = plot_evaluation_period_progression(math_analysis, por_analysis, figures_dir / "period_grade_progression.png")

    figure_paths = [fig1, fig2, fig3, fig4]
    print(f"[OK] Generated {len(figure_paths)} charts in {figures_dir}")
    for f in figure_paths:
        print(f"     - {f.name}")

    # 6. Generate Analytical Markdown Report
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_file = reports_dir / "analysis_report.md"
    generate_markdown_report(
        math_analysis=math_analysis,
        por_analysis=por_analysis,
        math_audit=math_audit,
        por_audit=por_audit,
        comparison=comparison,
        math_sha=math_sha,
        por_sha=por_sha,
        figure_paths=figure_paths,
        output_path=report_file,
        math_val_rep=math_val_rep,
        por_val_rep=por_val_rep,
    )
    print(f"[OK] Generated analytical report: {report_file}")
    print("=" * 70)
    print("Pipeline executed successfully.")
    return 0


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Student Performance Analyzer: Modular analysis of UCI academic cohorts."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory containing student-mat.csv and student-por.csv"
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("reports"),
        help="Directory where analysis_report.md will be generated"
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=Path("reports/figures"),
        help="Directory where visual charts will be saved"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_PASS_THRESHOLD,
        help="Pass threshold on G3 between 0.0 and 20.0 (default: 8.0, illustrative 40%% benchmark)"
    )

    args = parser.parse_args()
    exit_code = run_pipeline(
        data_dir=args.data_dir,
        reports_dir=args.reports_dir,
        figures_dir=args.figures_dir,
        threshold=args.threshold,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
