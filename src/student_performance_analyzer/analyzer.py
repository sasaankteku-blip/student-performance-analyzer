"""Statistical analysis and pass/fail evaluation for student performance."""

import math
from dataclasses import dataclass, field
import pandas as pd
from .constants import DEFAULT_PASS_THRESHOLD, STUDYTIME_LABELS, MIN_GRADE, MAX_GRADE


@dataclass
class GradeStats:
    """Summary statistics for an evaluation period grade."""
    count: int
    mean: float
    std: float
    median: float
    min_val: float
    max_val: float
    q25: float
    q75: float


@dataclass
class StudyTimeGroupStats:
    """Statistics for an ordinal study time category."""
    category: int
    label: str
    count: int
    percentage: float
    g3_mean: float
    g3_std: float
    g3_median: float
    pass_count: int
    pass_rate: float


@dataclass
class CourseAnalysis:
    """Comprehensive statistical analysis results for a single course cohort."""
    course_name: str
    total_records: int
    gradable_records: int
    ungradable_records: int
    pass_threshold: float
    pass_count: int
    fail_count: int
    pass_rate: float
    fail_rate: float
    g1_stats: GradeStats
    g2_stats: GradeStats
    g3_stats: GradeStats
    studytime_stats: list[StudyTimeGroupStats] = field(default_factory=list)


@dataclass
class CourseComparison:
    """Aggregate comparison between Mathematics and Portuguese courses.

    No individual student matching is performed; comparisons are strictly aggregate.
    """
    math_records: int
    por_records: int
    math_pass_rate: float
    por_pass_rate: float
    math_g3_mean: float
    por_g3_mean: float
    math_g3_median: float
    por_g3_median: float
    comparison_notes: list[str] = field(default_factory=list)


def calculate_grade_stats(series: pd.Series) -> GradeStats:
    """Calculate descriptive statistics for a grade series, filtering out invalid/missing scores."""
    numeric_s = pd.to_numeric(series, errors="coerce")
    clean = numeric_s.dropna()
    # Filter to valid score range [0, 20]
    valid_scores = clean[(clean >= MIN_GRADE) & (clean <= MAX_GRADE)]

    if len(valid_scores) == 0:
        return GradeStats(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    return GradeStats(
        count=int(len(valid_scores)),
        mean=float(valid_scores.mean()),
        std=float(valid_scores.std(ddof=1)) if len(valid_scores) > 1 else 0.0,
        median=float(valid_scores.median()),
        min_val=float(valid_scores.min()),
        max_val=float(valid_scores.max()),
        q25=float(valid_scores.quantile(0.25)),
        q75=float(valid_scores.quantile(0.75)),
    )


def evaluate_course_performance(
    df: pd.DataFrame,
    course_name: str,
    threshold: float = DEFAULT_PASS_THRESHOLD,
) -> tuple[pd.DataFrame, CourseAnalysis]:
    """Evaluate academic performance for a single course cohort.

    Rules enforced:
    - G3 is the primary evaluation score.
    - Passing rule: G3 >= threshold (configurable, default 8.0 / 20).
    - Never average G1/G2/G3 for the pass decision.
    - studytime treated strictly as ordinal categories.
    """
    if not isinstance(threshold, (int, float)) or math.isnan(threshold) or math.isinf(threshold) or not (MIN_GRADE <= threshold <= MAX_GRADE):
        raise ValueError(
            f"Invalid pass threshold '{threshold}'. "
            f"Threshold must be a finite number between {MIN_GRADE} and {MAX_GRADE}."
        )

    evaluated = df.copy()

    # Apply row-aligned boolean mask for gradable records
    if "is_gradable" in evaluated.columns:
        is_gradable_mask = evaluated["is_gradable"].fillna(False).astype(bool)
    else:
        # Precondition fallback: check G3 validity directly with a row-aligned Series mask
        g3_numeric = pd.to_numeric(evaluated["G3"], errors="coerce")
        is_gradable_mask = g3_numeric.notna() & (g3_numeric >= MIN_GRADE) & (g3_numeric <= MAX_GRADE)
        evaluated["is_gradable"] = is_gradable_mask

    gradable_df = evaluated[is_gradable_mask].copy()

    # Passed flag solely on G3 >= threshold
    gradable_g3 = pd.to_numeric(gradable_df["G3"], errors="coerce")
    gradable_df["passed"] = gradable_g3 >= threshold
    evaluated.loc[gradable_df.index, "passed"] = gradable_df["passed"]

    total_records = len(evaluated)
    gradable_count = len(gradable_df)
    ungradable_count = total_records - gradable_count

    pass_count = int(gradable_df["passed"].sum())
    fail_count = gradable_count - pass_count
    pass_rate = (pass_count / gradable_count * 100.0) if gradable_count > 0 else 0.0
    fail_rate = (fail_count / gradable_count * 100.0) if gradable_count > 0 else 0.0

    # Descriptive stats for periods, strictly using valid scores in [0, 20]
    g1_stats = calculate_grade_stats(gradable_df["G1"])
    g2_stats = calculate_grade_stats(gradable_df["G2"])
    g3_stats = calculate_grade_stats(gradable_df["G3"])

    # Studytime breakdown (ordinal categories 1, 2, 3, 4)
    studytime_list: list[StudyTimeGroupStats] = []
    for cat in sorted(STUDYTIME_LABELS.keys()):
        cat_df = gradable_df[gradable_df["studytime"] == cat]
        cat_count = len(cat_df)
        cat_pct = (cat_count / gradable_count * 100.0) if gradable_count > 0 else 0.0

        if cat_count > 0:
            cat_g3 = pd.to_numeric(cat_df["G3"], errors="coerce")
            cat_mean = float(cat_g3.mean())
            cat_std = float(cat_g3.std(ddof=1)) if cat_count > 1 else 0.0
            cat_median = float(cat_g3.median())
            cat_pass = int(cat_df["passed"].sum())
            cat_pass_rate = float(cat_pass / cat_count * 100.0)
        else:
            cat_mean = 0.0
            cat_std = 0.0
            cat_median = 0.0
            cat_pass = 0
            cat_pass_rate = 0.0

        studytime_list.append(
            StudyTimeGroupStats(
                category=cat,
                label=STUDYTIME_LABELS[cat],
                count=cat_count,
                percentage=cat_pct,
                g3_mean=cat_mean,
                g3_std=cat_std,
                g3_median=cat_median,
                pass_count=cat_pass,
                pass_rate=cat_pass_rate,
            )
        )

    analysis = CourseAnalysis(
        course_name=course_name,
        total_records=total_records,
        gradable_records=gradable_count,
        ungradable_records=ungradable_count,
        pass_threshold=threshold,
        pass_count=pass_count,
        fail_count=fail_count,
        pass_rate=pass_rate,
        fail_rate=fail_rate,
        g1_stats=g1_stats,
        g2_stats=g2_stats,
        g3_stats=g3_stats,
        studytime_stats=studytime_list,
    )

    return evaluated, analysis


def compare_cohorts(math: CourseAnalysis, por: CourseAnalysis) -> CourseComparison:
    """Produce aggregate comparison between Mathematics and Portuguese cohorts."""
    notes = [
        f"Mathematics cohort size: N={math.total_records}; Portuguese cohort size: N={por.total_records}.",
        f"Mathematics pass rate (G3 >= {math.pass_threshold:.1f}/20): {math.pass_rate:.1f}% ({math.pass_count}/{math.gradable_records}).",
        f"Portuguese pass rate (G3 >= {por.pass_threshold:.1f}/20): {por.pass_rate:.1f}% ({por.pass_count}/{por.gradable_records}).",
        f"Mathematics mean G3: {math.g3_stats.mean:.2f} (median {math.g3_stats.median:.1f}); Portuguese mean G3: {por.g3_stats.mean:.2f} (median {por.g3_stats.median:.1f}).",
        "Cohort comparison is strictly aggregate. Records were not merged or linked across files."
    ]

    return CourseComparison(
        math_records=math.total_records,
        por_records=por.total_records,
        math_pass_rate=math.pass_rate,
        por_pass_rate=por.pass_rate,
        math_g3_mean=math.g3_stats.mean,
        por_g3_mean=por.g3_stats.mean,
        math_g3_median=math.g3_stats.median,
        por_g3_median=por.g3_stats.median,
        comparison_notes=notes,
    )
