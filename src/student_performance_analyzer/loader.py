"""CSV Data Loader for UCI Student Performance datasets."""

from pathlib import Path
import pandas as pd


def load_student_csv(filepath: str | Path, delimiter: str = ";") -> pd.DataFrame:
    """Load a raw student performance CSV file.

    Args:
        filepath: Path to the CSV file.
        delimiter: Delimiter character (default ';').

    Returns:
        Raw pandas DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is empty or cannot be parsed.
    """
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"Dataset file not found at: {path}")

    if path.stat().st_size == 0:
        raise ValueError(f"Dataset file is empty (0 bytes): {path}")

    try:
        df = pd.read_csv(path, sep=delimiter, engine="python")
    except Exception as e:
        raise ValueError(f"Failed to parse CSV file {path}: {e}") from e

    if df.empty:
        raise ValueError(f"Loaded DataFrame is empty from {path}")

    return df
