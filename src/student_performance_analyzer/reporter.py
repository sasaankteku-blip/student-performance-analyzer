"""Markdown report generator for the Student Performance Analyzer."""

from datetime import datetime
from pathlib import Path
from .analyzer import CourseAnalysis, CourseComparison
from .cleaner import AuditReport
from .validator import ValidationReport
from .constants import (
    CITATION_DATASET,
    CITATION_PAPER,
    DATASET_DOI,
    DATASET_DOI_URL,
    DATASET_LICENSE,
    DATASET_LICENSE_URL,
    DATASET_NAME,
    DATASET_PUBLISHER,
    DATASET_URL,
    MAX_GRADE,
)


def generate_markdown_report(
    math_analysis: CourseAnalysis,
    por_analysis: CourseAnalysis,
    math_audit: AuditReport,
    por_audit: AuditReport,
    comparison: CourseComparison,
    math_sha: str,
    por_sha: str,
    figure_paths: list[Path],
    output_path: Path,
    math_val_rep: ValidationReport | None = None,
    por_val_rep: ValidationReport | None = None,
) -> Path:
    """Compile findings into an audit-friendly Markdown analytical report."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    threshold = math_analysis.pass_threshold
    threshold_pct = (threshold / MAX_GRADE) * 100.0

    lines: list[str] = []
    lines.append("# Student Performance Analysis Report")
    lines.append("")
    lines.append(f"- **Generated:** {now_str}")
    lines.append("- **Tool:** Student Performance Analyzer (Python CLI, modular architecture)")
    lines.append("- **Data Source:** UCI Machine Learning Repository (*Student Performance*)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Attribution Section
    lines.append("## 1. Dataset Provenance, Attribution, and Project Disclosure")
    lines.append("")
    lines.append(f"- **Dataset Title:** {DATASET_NAME}")
    lines.append(f"- **Publisher:** {DATASET_PUBLISHER}")
    lines.append(f"- **Official URL:** [{DATASET_URL}]({DATASET_URL})")
    lines.append(f"- **DOI:** [{DATASET_DOI}]({DATASET_DOI_URL})")
    lines.append(f"- **License:** [{DATASET_LICENSE}]({DATASET_LICENSE_URL})")
    lines.append(f"- **UCI Dataset Citation:** {CITATION_DATASET}")
    lines.append(f"- **Original Publication Citation:** {CITATION_PAPER}")
    lines.append("")
    lines.append("### Project Modifications and Governance Disclosure")
    lines.append("In compliance with CC BY 4.0 attribution requirements, the following project changes are disclosed:")
    lines.append("1. **Unmodified Source Files:** Raw CSV files (`student-mat.csv` and `student-por.csv`) are ingested without modifying underlying source records.")
    lines.append("2. **Surrogate Keys:** A sequential per-file surrogate key (e.g. `MAT_####`, `POR_####`) is assigned strictly for internal audit traceability. Neither file contains an official student ID.")
    lines.append(f"3. **Derived Outcome Flag:** A boolean `passed` flag was generated applying the project's illustrative benchmark (G3 >= {threshold:.1f} / 20).")
    lines.append("4. **Aggregate Output Only:** To safeguard student privacy and ensure ethical compliance, this report contains zero row-level student records or personal identifiable information.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Analytical Methodologies & Guardrails
    lines.append("## 2. Analytical Principles and Guardrails")
    lines.append("")
    lines.append("### 2.1 Course Independence and Demographic Non-Linking")
    lines.append(
        "The Mathematics (`student-mat.csv`) and Portuguese (`student-por.csv`) datasets are analyzed "
        "as parallel, independent cohorts. Although UCI documentation notes that 382 students overlap across courses, "
        "demographic matching is inherently imprecise and lacks an official student ID. "
        "**This project strictly forbids record-level merging or matching across files.**"
    )
    lines.append("")
    lines.append("### 2.2 Primary Outcome and Illustrative Pass Threshold")
    lines.append("- **Primary Metric:** `G3` (final period evaluation, 0–20 integer scale) serves as the sole outcome variable for the pass/fail evaluation.")
    lines.append("- **No Averaging:** `G1` and `G2` evaluate intermediate academic periods and are never averaged with `G3` to determine pass status.")
    lines.append(
        f"- **Illustrative Threshold ({threshold:.1f} / 20):** A student achieves an illustrative pass if G3 >= {threshold:.1f} out of 20. "
        f"This corresponds to {threshold_pct:.1f}% of the 0–20 grading scale and is an illustrative project threshold for analytical demonstration. "
        "**This benchmark represents this project's illustrative definition and does not represent an official school policy.**"
    )
    lines.append("")
    lines.append("### 2.3 Ordinal Weekly Study Time")
    lines.append(
        "The `studytime` attribute represents four binned interval categories (1: <2h, 2: 2–5h, 3: 5–10h, 4: >10h). "
        "It is treated strictly as an ordinal factor and never as continuous physical hours."
    )
    lines.append("")
    lines.append("### 2.4 Duplicate Detection Without Silent Deletion")
    lines.append(
        "All 33 raw features were audited for exact duplicate entries. Detected duplicates are logged and reported; "
        "rows are never silently removed or altered."
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Data Quality & Audit Findings
    lines.append("## 3. Data Ingestion & Quality Audit")
    lines.append("")

    # Extract invalid counts if ValidationReport provided
    m_inv_g1 = math_val_rep.out_of_range_g1 if math_val_rep else 0
    m_inv_g2 = math_val_rep.out_of_range_g2 if math_val_rep else 0
    m_inv_g3 = math_val_rep.out_of_range_g3 if math_val_rep else 0
    m_inv_st = math_val_rep.invalid_studytime if math_val_rep else 0

    p_inv_g1 = por_val_rep.out_of_range_g1 if por_val_rep else 0
    p_inv_g2 = por_val_rep.out_of_range_g2 if por_val_rep else 0
    p_inv_g3 = por_val_rep.out_of_range_g3 if por_val_rep else 0
    p_inv_st = por_val_rep.invalid_studytime if por_val_rep else 0

    lines.append("| Cohort / File | SHA-256 Checksum | Ingested Records | Exact Duplicates | Missing Values | Invalid Grades (G1/G2/G3) | Invalid Studytime | Gradable Records |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    lines.append(
        f"| **Mathematics** (`student-mat.csv`) | `{math_sha}` | {math_audit.total_records} | "
        f"{math_audit.exact_duplicates_count} | {sum(math_audit.missing_values_by_column.values())} | "
        f"{m_inv_g1} / {m_inv_g2} / {m_inv_g3} | {m_inv_st} | {math_analysis.gradable_records} |"
    )
    lines.append(
        f"| **Portuguese** (`student-por.csv`) | `{por_sha}` | {por_audit.total_records} | "
        f"{por_audit.exact_duplicates_count} | {sum(por_audit.missing_values_by_column.values())} | "
        f"{p_inv_g1} / {p_inv_g2} / {p_inv_g3} | {p_inv_st} | {por_analysis.gradable_records} |"
    )
    lines.append("")
    lines.append(f"- **Mathematics Audit Note:** {math_audit.audit_note} (Validation: Out-of-range G1={m_inv_g1}, G2={m_inv_g2}, G3={m_inv_g3}; Invalid studytime={m_inv_st})")
    lines.append(f"- **Portuguese Audit Note:** {por_audit.audit_note} (Validation: Out-of-range G1={p_inv_g1}, G2={p_inv_g2}, G3={p_inv_g3}; Invalid studytime={p_inv_st})")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Mathematics Course Performance
    lines.append("## 4. Mathematics Course Performance (`student-mat.csv`)")
    lines.append("")
    lines.append(f"- **Total Cohort Size:** {math_analysis.total_records} students")
    lines.append(
        f"- **Illustrative Pass Rate (G3 >= {threshold:.1f} / 20):** **{math_analysis.pass_rate:.1f}%** "
        f"({math_analysis.pass_count} passed, {math_analysis.fail_count} failed)"
    )
    lines.append("")
    lines.append("### Evaluation Period Grade Summary")
    lines.append("")
    lines.append("| Period | Metric | Mean | Std Dev | Median | Min | Max | Q25 | Q75 |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for name, s in [("G1", math_analysis.g1_stats), ("G2", math_analysis.g2_stats), ("G3 (Final)", math_analysis.g3_stats)]:
        lines.append(
            f"| **{name}** | Period Grade | {s.mean:.2f} | {s.std:.2f} | {s.median:.1f} | {s.min_val:.0f} | {s.max_val:.0f} | {s.q25:.1f} | {s.q75:.1f} |"
        )
    lines.append("")
    lines.append("### Study Time Ordinal Breakdown (Mathematics)")
    lines.append("")
    lines.append("| Category | Interval Description | Students | Cohort % | Mean G3 | Median G3 | Pass Rate |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for st in math_analysis.studytime_stats:
        lines.append(
            f"| **{st.category}** | {st.label} | {st.count} | {st.percentage:.1f}% | {st.g3_mean:.2f} | {st.g3_median:.1f} | {st.pass_rate:.1f}% |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Portuguese Course Performance
    lines.append("## 5. Portuguese Course Performance (`student-por.csv`)")
    lines.append("")
    lines.append(f"- **Total Cohort Size:** {por_analysis.total_records} students")
    lines.append(
        f"- **Illustrative Pass Rate (G3 >= {threshold:.1f} / 20):** **{por_analysis.pass_rate:.1f}%** "
        f"({por_analysis.pass_count} passed, {por_analysis.fail_count} failed)"
    )
    lines.append("")
    lines.append("### Evaluation Period Grade Summary")
    lines.append("")
    lines.append("| Period | Metric | Mean | Std Dev | Median | Min | Max | Q25 | Q75 |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for name, s in [("G1", por_analysis.g1_stats), ("G2", por_analysis.g2_stats), ("G3 (Final)", por_analysis.g3_stats)]:
        lines.append(
            f"| **{name}** | Period Grade | {s.mean:.2f} | {s.std:.2f} | {s.median:.1f} | {s.min_val:.0f} | {s.max_val:.0f} | {s.q25:.1f} | {s.q75:.1f} |"
        )
    lines.append("")
    lines.append("### Study Time Ordinal Breakdown (Portuguese)")
    lines.append("")
    lines.append("| Category | Interval Description | Students | Cohort % | Mean G3 | Median G3 | Pass Rate |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for st in por_analysis.studytime_stats:
        lines.append(
            f"| **{st.category}** | {st.label} | {st.count} | {st.percentage:.1f}% | {st.g3_mean:.2f} | {st.g3_median:.1f} | {st.pass_rate:.1f}% |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Aggregate Cross-Course Comparison
    lines.append("## 6. Aggregate Cross-Course Comparison")
    lines.append("")
    lines.append("| Dimension | Mathematics Cohort | Portuguese Cohort | Delta / Note |")
    lines.append("| :--- | :--- | :--- | :--- |")
    lines.append(
        f"| **Sample Size (N)** | {comparison.math_records} | {comparison.por_records} | "
        f"Portuguese has {comparison.por_records - comparison.math_records} more instances |"
    )
    lines.append(
        f"| **Pass Rate (G3 >= {threshold:.1f}/20)** | {comparison.math_pass_rate:.1f}% | {comparison.por_pass_rate:.1f}% | "
        f"Portuguese pass rate is +{comparison.por_pass_rate - comparison.math_pass_rate:.1f} percentage points higher |"
    )
    lines.append(
        f"| **Final Grade Mean (G3)** | {comparison.math_g3_mean:.2f} | {comparison.por_g3_mean:.2f} | "
        f"Portuguese mean is +{comparison.por_g3_mean - comparison.math_g3_mean:.2f} points higher |"
    )
    lines.append(
        f"| **Final Grade Median (G3)** | {comparison.math_g3_median:.1f} | {comparison.por_g3_median:.1f} | "
        f"Portuguese median is +{comparison.por_g3_median - comparison.math_g3_median:.1f} points higher |"
    )
    lines.append("")
    lines.append("### Key Comparative Observations")
    for note in comparison.comparison_notes:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Visual Figures Section
    lines.append("## 7. Analytical Visualizations")
    lines.append("")
    for fig in figure_paths:
        rel_path = f"figures/{fig.name}"
        title = fig.stem.replace("_", " ").title()
        lines.append(f"### {title}")
        lines.append(f"![{title}]({rel_path})")
        lines.append("")
    lines.append("---")
    lines.append("")

    # Disclaimer & Limitations
    lines.append("## 8. Limitations and Non-Causal Disclaimer")
    lines.append("")
    lines.append("1. **Exploratory Scope:** This analysis provides descriptive cohort statistics and exploratory comparisons. It makes no predictive claims, causal inferences, or automated interventions.")
    lines.append("2. **Independent Sampling:** As established in project methodology, Mathematics and Portuguese cohorts are analyzed as separate entities without student-level linkage.")
    lines.append("3. **Illustrative Benchmark:** The configured threshold is purely an illustrative benchmark for analytical demonstration and does not reflect an official school policy.")
    lines.append("")

    content = "\n".join(lines)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path
