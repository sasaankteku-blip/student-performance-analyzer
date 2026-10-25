"""Data validation and surrogate key assignment for Student Performance records."""

from dataclasses import dataclass, field
import pandas as pd
from .constants import EXPECTED_COLUMNS, MAX_GRADE, MIN_GRADE


@dataclass
class ValidationReport:
    """Summary of schema and record validation findings."""
    course_name: str
    total_records: int
    missing_columns: list[str] = field(default_factory=list)
    extra_columns: list[str] = field(default_factory=list)
    out_of_range_g1: int = 0
    out_of_range_g2: int = 0
    out_of_range_g3: int = 0
    invalid_studytime: int = 0
    ungradable_records: int = 0
    gradable_records: int = 0

    @property
    def is_schema_valid(self) -> bool:
        return len(self.missing_columns) == 0


def validate_schema(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Check if the DataFrame contains all expected columns."""
    existing_cols = set(df.columns)
    expected_set = set(EXPECTED_COLUMNS)
    missing = [col for col in EXPECTED_COLUMNS if col not in existing_cols]
    extra = [col for col in df.columns if col not in expected_set]
    return missing, extra


def validate_and_assign_keys(
    df: pd.DataFrame,
    course_name: str,
    prefix: str = "ROW"
) -> tuple[pd.DataFrame, ValidationReport]:
    """Validate DataFrame records, assign sequential surrogate keys, and flag invalid entries.

    Surrogate keys are generated per file (e.g. MAT_0001) for audit traceability.
    Demographic matching across files is strictly prohibited.
    """
    missing_cols, extra_cols = validate_schema(df)
    total_records = len(df)

    report = ValidationReport(
        course_name=course_name,
        total_records=total_records,
        missing_columns=missing_cols,
        extra_columns=extra_cols,
    )

    if not report.is_schema_valid:
        raise ValueError(
            f"Schema validation failed for {course_name}. Missing columns: {missing_cols}"
        )

    validated = df.copy()

    # Assign surrogate key strictly for row-level tracing and audit reporting
    validated["surrogate_key"] = [f"{prefix}_{i+1:04d}" for i in range(total_records)]

    # Check score ranges
    for grade_col in ["G1", "G2", "G3"]:
        numeric_series = pd.to_numeric(validated[grade_col], errors="coerce")
        validated[grade_col] = numeric_series

    invalid_g1 = validated["G1"].isna() | (validated["G1"] < MIN_GRADE) | (validated["G1"] > MAX_GRADE)
    invalid_g2 = validated["G2"].isna() | (validated["G2"] < MIN_GRADE) | (validated["G2"] > MAX_GRADE)
    invalid_g3 = validated["G3"].isna() | (validated["G3"] < MIN_GRADE) | (validated["G3"] > MAX_GRADE)

    report.out_of_range_g1 = int(invalid_g1.sum())
    report.out_of_range_g2 = int(invalid_g2.sum())
    report.out_of_range_g3 = int(invalid_g3.sum())

    # Studytime validation (must be integer 1, 2, 3, or 4)
    valid_studytime = validated["studytime"].isin([1, 2, 3, 4])
    report.invalid_studytime = int((~valid_studytime).sum())

    # Flag records as gradable or ungradable based on G3 validity
    # (G3 is the sole primary score for the pass/fail policy)
    validated["is_gradable"] = ~invalid_g3
    report.gradable_records = int(validated["is_gradable"].sum())
    report.ungradable_records = int((~validated["is_gradable"]).sum())

    return validated, report
