import pandas as pd


def aggregate_daily_tickets(
    tickets: pd.DataFrame,
    timestamp_column: str,
    category_column: str,
    categories: list[str],
) -> pd.DataFrame:
    """Count tickets by calendar date and category."""
    work = tickets.copy()
    work["date"] = work[timestamp_column].dt.normalize()

    counts = (
        work.groupby(["date", category_column])
        .size()
        .unstack(fill_value=0)
    )

    counts = counts.reindex(columns=categories, fill_value=0)
    counts = counts.sort_index()
    counts["Total"] = counts.sum(axis=1)

    return counts


def make_complete_daily_counts(
    daily_counts: pd.DataFrame,
    end_date: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """
    Add missing calendar dates.

    This assumes a missing date means zero tickets. Confirm data completeness
    before using this assumption.
    """
    if daily_counts.empty:
        raise ValueError("No daily ticket counts are available.")

    final_date = end_date or daily_counts.index.max()
    full_index = pd.date_range(
        daily_counts.index.min(),
        pd.Timestamp(final_date).normalize(),
        freq="D",
        name="date",
    )

    return daily_counts.reindex(full_index, fill_value=0)


def add_calendar_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add weekday and calendar fields to a date-indexed table."""
    result = frame.copy()
    result["day_of_week"] = result.index.dayofweek
    result["day_name"] = result.index.day_name()
    result["is_weekend"] = (result.index.dayofweek >= 5).astype(int)
    result["month"] = result.index.month
    result["day_of_month"] = result.index.day
    return result
