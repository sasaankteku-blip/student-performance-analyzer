"""Constants and configuration for the Student Performance Analyzer."""

from typing import Final

EXPECTED_COLUMNS: Final[list[str]] = [
    "school", "sex", "age", "address", "famsize", "Pstatus",
    "Medu", "Fedu", "Mjob", "Fjob", "reason", "guardian",
    "traveltime", "studytime", "failures", "schoolsup", "famsup",
    "paid", "activities", "nursery", "higher", "internet",
    "romantic", "famrel", "freetime", "goout", "Dalc", "Walc",
    "health", "absences", "G1", "G2", "G3"
]

MIN_GRADE: Final[int] = 0
MAX_GRADE: Final[int] = 20

DEFAULT_PASS_THRESHOLD: Final[float] = 8.0

STUDYTIME_LABELS: Final[dict[int, str]] = {
    1: "< 2 hours",
    2: "2 - 5 hours",
    3: "5 - 10 hours",
    4: "> 10 hours"
}

DATASET_NAME: Final[str] = "Student Performance"
DATASET_PUBLISHER: Final[str] = "UCI Machine Learning Repository"
DATASET_DOI: Final[str] = "10.24432/C5TG7T"
DATASET_DOI_URL: Final[str] = "https://doi.org/10.24432/C5TG7T"
DATASET_URL: Final[str] = "https://archive.ics.uci.edu/dataset/320/student+performance"
DATASET_LICENSE: Final[str] = "Creative Commons Attribution 4.0 International (CC BY 4.0)"
DATASET_LICENSE_URL: Final[str] = "https://creativecommons.org/licenses/by/4.0/"
CITATION_DATASET: Final[str] = (
    "Cortez, P. (2008). Student Performance [Dataset]. "
    "UCI Machine Learning Repository. https://doi.org/10.24432/C5TG7T"
)
CITATION_PAPER: Final[str] = (
    "Cortez, P., & Silva, A. (2008). Using data mining to predict secondary "
    "school student performance. Proceedings of the 5th Annual Future Business "
    "Technology Conference (FUBUTEC 2008), pp. 5-12."
)
