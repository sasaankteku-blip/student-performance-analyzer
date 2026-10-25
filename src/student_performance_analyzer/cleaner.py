"""Data cleaner and audit reporter for Student Performance datasets."""

from dataclasses import dataclass, field
import pandas as pd
from .constants import EXPECTED_COLUMNS


@dataclass
class AuditReport:
    """Audit summary for data cleaning and duplicate detection."""
    course_name: str
    total_records: int
    exact_duplicates_count: int
    duplicate_indices: list[int] = field(default_factory=list)
    missing_values_by_column: dict[str, int] = field(default_factory=dict)
    records_retained: int = 0
    audit_note: str = ""


def audit_and_clean_records(
    df: pd.DataFrame,
    course_name: str
) -> tuple[pd.DataFrame, AuditReport]:
    """Audit dataset records for exact duplicates and missing values.

    CRITICAL REQUIREMENT:
    Exact duplicates are detected and recorded for audit logging, but rows are
    NEVER silently dropped or deduplicated by demographic attributes.
    All records are retained to maintain raw provenance traceability.
    """
    total_records = len(df)

    # Check exact duplicates based strictly on original 33 dataset columns
    feature_cols = [c for c in EXPECTED_COLUMNS if c in df.columns]
    dup_mask = df.duplicated(subset=feature_cols, keep="first")
    exact_dup_count = int(dup_mask.sum())
    dup_indices = df.index[dup_mask].tolist()

    # Check missing values
    missing_counts = {
        col: int(df[col].isna().sum())
        for col in feature_cols
        if df[col].isna().sum() > 0
    }

    cleaned = df.copy()
    cleaned["is_exact_duplicate"] = dup_mask

    audit_note = (
        f"{course_name}: {total_records} rows audited. "
        f"{exact_dup_count} exact duplicates detected. "
        f"All rows preserved without silent deletion."
    )

    report = AuditReport(
        course_name=course_name,
        total_records=total_records,
        exact_duplicates_count=exact_dup_count,
        duplicate_indices=dup_indices,
        missing_values_by_column=missing_counts,
        records_retained=total_records,
        audit_note=audit_note,
    )

    return cleaned, report
