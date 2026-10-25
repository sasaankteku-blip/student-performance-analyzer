# Student Performance Analyzer

A modular, defensive Python command-line application for analyzing secondary school student academic performance from the UCI Machine Learning Repository. The analyzer validates datasets against a strict 33-column schema, audits duplicates without silent deletion, calculates independent cohort statistics across Mathematics and Portuguese courses, evaluates illustrative pass benchmarks on final grades, generates publication-quality visualizations, and compiles privacy-preserving aggregate Markdown reports.

## Features

- **Robust CSV Ingestion:** Ingests semicolon-delimited CSV files with comprehensive file existence, emptiness, and delimiter parsing checks.
- **Strict Schema & Range Validation:** Enforces the official 33-feature schema, validates score boundaries (0 <= grade <= 20), flags ungradable rows, and assigns internal surrogate keys (`MAT_####`, `POR_####`) for audit traceability.
- **Non-Destructive Quality Auditing:** Detects exact duplicate records across all 33 attributes, logging them for audit review without silently dropping or altering records.
- **Strict Cohort Separation:** Evaluates Mathematics (N=395) and Portuguese (N=649) cohorts as independent datasets without demographic cross-linking or assumptions.
- **Independent Descriptive Statistics:** Computes mean, median, standard deviation, min, max, and interquartile ranges (Q25, Q75) for evaluation periods G1, G2, and final evaluation G3.
- **Final-Grade Outcome Evaluation:** Evaluates pass/fail rates strictly on final grade G3 against a configurable threshold; period grades G1 and G2 are never averaged with G3.
- **Ordinal Study Time Analysis:** Treats weekly study time strictly as four ordinal binned intervals (<2h, 2-5h, 5-10h, >10h) rather than continuous hours.
- **Automated Publication Visualizations:** Generates headless Matplotlib and Seaborn figures illustrating grade distributions, pass rates, study time relationships, and period score progression.
- **Privacy-Preserving Aggregate Reporting:** Produces an audit-ready Markdown report containing cohort-level statistics with zero individual student-level data exposure.

## Pipeline Architecture

The application is structured into decoupled, single-responsibility modules:

```text
               ┌────────────────────────────────────────────────────────┐
               │                data/raw/*.csv                          │
               │   (student-mat.csv [N=395], student-por.csv [N=649])    │
               └───────────────────────────┬────────────────────────────┘
                                           │
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │             Ingestion & I/O (loader.py)                │
               │        Delimiter verification, error handling          │
               └───────────────────────────┬────────────────────────────┘
                                           │
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │       Schema Validation & Keying (validator.py)        │
               │   33 columns, 0-20 score bounds, MAT_#### / POR_####   │
               └───────────────────────────┬────────────────────────────┘
                                           │
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │      Quality Audit & Duplicate Audit (cleaner.py)      │
               │    Exact duplicate detection, row-preservation audit   │
               └───────────────────────────┬────────────────────────────┘
                                           │
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │      Statistical & Outcome Analysis (analyzer.py)      │
               │  G1/G2/G3 metrics, G3 threshold evaluation, study time │
               └───────────────┬────────────────────────┬───────────────┘
                               │                        │
                               ▼                        ▼
        ┌──────────────────────────────┐ ┌──────────────────────────────┐
        │   Visualizer (visualizer.py) │ │     Reporter (reporter.py)   │
        │   Headless chart generation  │ │   Audit Markdown reporting   │
        └──────────────┬───────────────┘ └──────────────┬───────────────┘
                       │                                │
                       ▼                                ▼
        ┌──────────────────────────────┐ ┌──────────────────────────────┐
        │   reports/figures/*.png      │ │  reports/analysis_report.md   │
        └──────────────────────────────┘ └──────────────────────────────┘
```

- `loader.py`: Ingests delimited CSV files with path validation and empty-file checks.
- `validator.py`: Verifies the 33 expected columns, checks grade and ordinal ranges, and assigns surrogate tracking keys.
- `cleaner.py`: Audits for identical records across all 33 features, recording occurrences while preserving every row.
- `analyzer.py`: Computes course-level summary statistics, evaluates pass outcomes based strictly on G3, summarizes ordinal study time brackets, and calculates cohort deltas.
- `visualizer.py`: Creates four publication-grade charts headlessly with consistent styling.
- `reporter.py`: Compiles findings, metadata, citations, and data governance disclosures into a clean Markdown report.
- `cli.py`: Exposes a parameterizable command-line interface (`--data-dir`, `--reports-dir`, `--figures-dir`, `--threshold`).

## Tech Stack

| Technology | Specification | Purpose |
| --- | --- | --- |
| **Python** | `>=3.10` (Tested on 3.14.4) | Core language runtime |
| **pandas** | `>=2.0` | Ingestion, validation, and statistical aggregation |
| **matplotlib** | `>=3.7` | Headless chart creation and visual styling |
| **seaborn** | `>=0.12` | Statistical distributions and comparative plotting |
| **pytest** | `>=7.0` | Comprehensive unit and integration testing suite |
| **setuptools** | `>=61.0` | Standards-compliant packaging via `pyproject.toml` |

## Setup & Installation

Clone or download the repository into your local environment:

```bash
git clone <repository-url>
cd student-performance-analyzer

# 1. Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Upgrade pip and install project dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Install the project package in editable mode
pip install -e .
```

## Obtaining the UCI Dataset

The analysis requires the official raw CSV files from the UCI Machine Learning Repository:

- **Dataset:** Student Performance
- **Publisher:** UCI Machine Learning Repository
- **DOI:** [10.24432/C5TG7T](https://doi.org/10.24432/C5TG7T)
- **Official Dataset Page:** [https://archive.ics.uci.edu/dataset/320/student+performance](https://archive.ics.uci.edu/dataset/320/student+performance)
- **Direct Archive Download:** [student+performance.zip](https://archive.ics.uci.edu/static/public/320/student%2Bperformance.zip)

### Expected Directory & File Names

Download `student+performance.zip`, extract its contents, and place the two semicolon-delimited CSV files in `data/raw/`:

```text
data/
└── raw/
    ├── student-mat.csv    # Mathematics course (395 records, 33 features)
    └── student-por.csv    # Portuguese language course (649 records, 33 features)
```

> **Note:** The `.gitignore` is configured to keep all raw and processed CSV data files strictly local, ensuring source data files are never committed to version control.

## CLI Usage

Run the end-to-end pipeline using the installed console script or directly through the Python module:

```bash
# Run using the console script
student-performance-analyzer --data-dir data/raw --reports-dir reports --figures-dir reports/figures --threshold 8.0

# Or execute via the Python module
python -m student_performance_analyzer --data-dir data/raw --reports-dir reports --figures-dir reports/figures --threshold 8.0
```

### CLI Arguments

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `--data-dir` | Path | `data/raw` | Path to directory containing `student-mat.csv` and `student-por.csv` |
| `--reports-dir` | Path | `reports` | Target directory for generated Markdown report (`analysis_report.md`) |
| `--figures-dir` | Path | `reports/figures` | Target directory for generated visualization charts (`.png`) |
| `--threshold` | Float | `8.0` | Pass benchmark on G3 (0.0 <= threshold <= 20.0, illustrative 40% benchmark) |

## Analytical Results (Benchmark: G3 >= 8.0 / 20)

At the illustrative threshold of **G3 >= 8.0 / 20** (40.0% of the maximum 20-point scale), the pipeline evaluates the two cohorts as follows:

| Metric | Mathematics Cohort (`student-mat.csv`) | Portuguese Cohort (`student-por.csv`) | Comparison Delta |
| :--- | :--- | :--- | :--- |
| **Total Cohort Size (N)** | 395 students | 649 students | Portuguese cohort has +254 records |
| **Illustrative Pass Rate** | **82.3%** (325 passed, 70 failed) | **95.4%** (619 passed, 30 failed) | Portuguese pass rate is **+13.1 percentage points higher** |
| **G3 Final Grade Mean** | 10.42 (std dev: 4.58) | 11.91 (std dev: 3.23) | Portuguese mean is **+1.49 points higher** |
| **G3 Final Grade Median** | 11.0 (Q25: 8.0, Q75: 14.0) | 12.0 (Q25: 10.0, Q75: 14.0) | Portuguese median is **+1.0 point higher** |
| **G1 First Period Mean** | 10.91 (std dev: 3.32) | 11.40 (std dev: 2.75) | Portuguese G1 is +0.49 points higher |
| **G2 Second Period Mean** | 10.71 (std dev: 3.76) | 11.57 (std dev: 2.91) | Portuguese G2 is +0.86 points higher |
| **Exact Duplicates Detected** | 0 (all 395 rows preserved) | 0 (all 649 rows preserved) | Zero rows dropped or modified |

### Ordinal Study Time Breakdown

Weekly study time is evaluated across four binned categories:

- **Mathematics:**
  - `< 2 hours` (N=105, 26.6%): Mean G3 = 10.05, Pass Rate = 79.0%
  - `2 - 5 hours` (N=198, 50.1%): Mean G3 = 10.17, Pass Rate = 81.3%
  - `5 - 10 hours` (N=65, 16.5%): Mean G3 = 11.40, Pass Rate = 89.2%
  - `> 10 hours` (N=27, 6.8%): Mean G3 = 11.26, Pass Rate = 85.2%
- **Portuguese:**
  - `< 2 hours` (N=212, 32.7%): Mean G3 = 10.84, Pass Rate = 91.5%
  - `2 - 5 hours` (N=305, 47.0%): Mean G3 = 12.09, Pass Rate = 96.4%
  - `5 - 10 hours` (N=97, 14.9%): Mean G3 = 13.23, Pass Rate = 100.0%
  - `> 10 hours` (N=35, 5.4%): Mean G3 = 13.06, Pass Rate = 97.1%

### Illustrative-Threshold Caveat

> **Important Caveat:** The pass threshold of **G3 >= 8.0 / 20** (40.0%) is an **illustrative project benchmark** chosen for analytical demonstration; it does **not** represent an official school policy. Pass/fail determination is based strictly on final period evaluation `G3`; intermediate period evaluations `G1` and `G2` are not averaged with `G3` for the pass decision.

## Visualizations

The pipeline produces four visual artifacts saved to `reports/figures/`:

### 1. Final Grade Distributions
Histograms with kernel density estimates (KDE) and threshold marker for Mathematics and Portuguese cohorts:

![Grade Distributions](reports/figures/grade_distributions.png)

### 2. Pass Rates Comparison
Comparative bar chart of illustrative pass and fail percentages across both courses:

![Pass Rates Comparison](reports/figures/pass_rates_comparison.png)

### 3. Weekly Study Time vs. Performance
Mean final grade across the four ordinal weekly study time brackets:

![Study Time Performance](reports/figures/studytime_performance.png)

### 4. Period Grade Progression
Mean score trajectories across evaluation periods G1, G2, and final G3:

![Period Grade Progression](reports/figures/period_grade_progression.png)

## Automated Test Suite

The test suite contains **23 automated unit and integration tests** executed with `pytest`:

```bash
pytest -v
```

### Test Suite Structure

- `tests/test_loader.py` (4 tests): CSV loading, delimiter parsing, empty file validation, and missing file exception handling.
- `tests/test_validator.py` (4 tests): 33-column schema verification, surrogate key assignment, range validation (0 <= grade <= 20), and ungradable record isolation.
- `tests/test_cleaner.py` (2 tests): Exact duplicate detection across all 33 features and row preservation without silent deletion.
- `tests/test_analyzer.py` (6 tests): Descriptive statistics, boundary conditions (G3=7 fails, G3=8 passes), non-averaging of G1/G2 with G3, ordinal study time aggregation, and cross-course comparisons.
- `tests/test_visualizer.py` (1 test): Headless rendering and validation of all four chart PNG files.
- `tests/test_reporter.py` (3 tests): Markdown report synthesis, dynamic threshold reporting, and attribution checks.
- `tests/test_cli.py` (3 tests): Argument handling, missing file diagnostics, and validation of illegal threshold inputs (negative, >20, NaN, inf).

## Limitations & Non-Causal Disclaimer

1. **Descriptive and Exploratory Scope:** This project provides descriptive cohort statistics and exploratory comparisons. It makes no causal inferences, predictive assertions, or automated student-level determinations.
2. **Cohort Separation:** Mathematics and Portuguese datasets are evaluated as independent cohorts. While UCI notes 382 overlapping students, demographic matching is ambiguous and lacks official unique IDs; records are never linked or merged across files.
3. **Non-Destructive Audit:** Duplicate records are audited and logged for review; no rows are silently removed or modified.
4. **Aggregate Privacy:** All published outputs and reports present aggregate cohort metrics only, with zero individual student-level data exposure.

## Data Attribution & Licensing

- **Dataset:** Student Performance, UCI Machine Learning Repository
- **DOI:** [10.24432/C5TG7T](https://doi.org/10.24432/C5TG7T)
- **Data License:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
- **Dataset Citation:** Cortez, P. (2008). *Student Performance* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5TG7T.
- **Original Publication Citation:** Cortez, P., & Silva, A. (2008). *Using data mining to predict secondary school student performance*. Proceedings of the 5th Annual Future Business Technology Conference (FUBUTEC 2008), pages 5–12.
- **Project Code License:** The source code license for this project is currently unspecified.