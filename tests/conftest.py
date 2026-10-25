"""Pytest fixtures for Student Performance Analyzer test suite."""

import pytest
import pandas as pd
from student_performance_analyzer.constants import EXPECTED_COLUMNS


@pytest.fixture
def minimal_valid_row():
    """Return a single valid student record matching the 33-column schema."""
    return {
        "school": "GP",
        "sex": "F",
        "age": 17,
        "address": "U",
        "famsize": "GT3",
        "Pstatus": "T",
        "Medu": 4,
        "Fedu": 4,
        "Mjob": "health",
        "Fjob": "teacher",
        "reason": "course",
        "guardian": "mother",
        "traveltime": 1,
        "studytime": 2,
        "failures": 0,
        "schoolsup": "no",
        "famsup": "yes",
        "paid": "no",
        "activities": "yes",
        "nursery": "yes",
        "higher": "yes",
        "internet": "yes",
        "romantic": "no",
        "famrel": 4,
        "freetime": 3,
        "goout": 3,
        "Dalc": 1,
        "Walc": 1,
        "health": 4,
        "absences": 2,
        "G1": 10,
        "G2": 11,
        "G3": 12,
    }


@pytest.fixture
def sample_dataframe(minimal_valid_row):
    """Return a DataFrame with 5 varied student records."""
    rows = []
    # Row 1: G3=12 (passes)
    r1 = dict(minimal_valid_row)
    r1["G3"] = 12
    r1["studytime"] = 2
    rows.append(r1)

    # Row 2: G3=8 (boundary: passes)
    r2 = dict(minimal_valid_row)
    r2["age"] = 16
    r2["G3"] = 8
    r2["studytime"] = 1
    rows.append(r2)

    # Row 3: G3=7 (boundary: fails)
    r3 = dict(minimal_valid_row)
    r3["age"] = 18
    r3["G3"] = 7
    r3["studytime"] = 3
    rows.append(r3)

    # Row 4: G3=0 (extreme minimum: fails)
    r4 = dict(minimal_valid_row)
    r4["age"] = 19
    r4["G3"] = 0
    r4["studytime"] = 4
    rows.append(r4)

    # Row 5: G3=20 (extreme maximum: passes)
    r5 = dict(minimal_valid_row)
    r5["age"] = 15
    r5["G3"] = 20
    r5["studytime"] = 2
    rows.append(r5)

    return pd.DataFrame(rows, columns=EXPECTED_COLUMNS)
