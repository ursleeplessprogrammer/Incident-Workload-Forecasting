from pathlib import Path

import pandas as pd


def load_tickets(
    path: Path,
    timestamp_column: str,
    category_column: str,
    timezone: str,
) -> pd.DataFrame:
    """Load ticket-level data and standardize timestamps and categories."""
    if not path.exists():
        raise FileNotFoundError(
            f"Ticket file not found: {path}\n"
            "Create data/daily_tickets.csv or update config.py."
        )

    data = pd.read_csv(path)

    required = {timestamp_column, category_column}
    missing = required - set(data.columns)

    if missing:
        raise ValueError(
            f"Ticket CSV is missing required columns: {sorted(missing)}"
        )

    if data.empty:
        raise ValueError("Ticket CSV contains no rows.")

    data = data.copy()
    data[timestamp_column] = pd.to_datetime(
        data[timestamp_column],
        errors="coerce",
        utc=True,
    )

    invalid_timestamps = int(data[timestamp_column].isna().sum())
    if invalid_timestamps:
        print(f"Warning: dropping {invalid_timestamps} rows with invalid timestamps.")
        data = data.dropna(subset=[timestamp_column])

    if data.empty:
        raise ValueError("No valid ticket timestamps remain.")

    data[timestamp_column] = (
        data[timestamp_column]
        .dt.tz_convert(timezone)
        .dt.tz_localize(None)
    )

    data[category_column] = (
        data[category_column]
        .astype("string")
        .str.strip()
    )

    return data


def load_conditions(path: Path | None, timezone: str) -> pd.DataFrame:
    """Load optional date-level condition flags."""
    if path is None or not path.exists():
        return pd.DataFrame(index=pd.DatetimeIndex([], name="date"))

    conditions = pd.read_csv(path)

    if "date" not in conditions.columns:
        raise ValueError("Conditions CSV must contain a 'date' column.")

    conditions = conditions.copy()
    conditions["date"] = pd.to_datetime(
        conditions["date"],
        errors="coerce",
        utc=True,
    )

    if conditions["date"].isna().any():
        raise ValueError("Conditions CSV contains invalid dates.")

    conditions["date"] = (
        conditions["date"]
        .dt.tz_convert(timezone)
        .dt.tz_localize(None)
        .dt.normalize()
    )

    conditions = conditions.set_index("date").sort_index()

    if conditions.index.has_duplicates:
        raise ValueError(
            "Conditions CSV must contain at most one row per date."
        )

    for column in conditions.columns:
        conditions[column] = pd.to_numeric(
            conditions[column],
            errors="coerce",
        ).fillna(0)

    return conditions
