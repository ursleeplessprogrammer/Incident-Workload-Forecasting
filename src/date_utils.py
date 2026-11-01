import pandas as pd


DAY_NAMES = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def complete_daily_index(
    first_date: pd.Timestamp,
    last_date: pd.Timestamp,
) -> pd.DatetimeIndex:
    """Return a complete daily date range, including all seven weekdays."""
    return pd.date_range(
        start=first_date.normalize(),
        end=last_date.normalize(),
        freq="D",
        name="date",
    )


def previous_complete_weekdays(
    anchor_date: pd.Timestamp,
    weeks: int,
) -> pd.DatetimeIndex:
    """
    Return the prior complete Monday–Sunday weeks before anchor_date.

    The returned dates exclude the week containing anchor_date.
    """
    anchor_date = pd.Timestamp(anchor_date).normalize()

    current_monday = anchor_date - pd.Timedelta(days=anchor_date.weekday())
    end_date = current_monday - pd.Timedelta(days=1)
    start_date = end_date - pd.Timedelta(days=weeks * 7 - 1)

    return pd.date_range(start_date, end_date, freq="D", name="date")


def same_calendar_dates_last_year(
    dates: pd.DatetimeIndex,
) -> pd.DatetimeIndex:
    """
    Return prior-year calendar-date equivalents.

    February 29 maps to February 28 in a non-leap year.
    """
    mapped = []

    for date in dates:
        try:
            mapped.append(date.replace(year=date.year - 1))
        except ValueError:
            mapped.append(date.replace(year=date.year - 1, day=28))

    return pd.DatetimeIndex(mapped, name="date")
