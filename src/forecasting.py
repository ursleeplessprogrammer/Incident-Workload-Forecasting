import numpy as np
import pandas as pd

from src.date_utils import previous_complete_weekdays


def weekday_history(
    daily_counts: pd.DataFrame,
    anchor_date: pd.Timestamp,
    category: str,
    lookback_weeks: int,
) -> pd.DataFrame:
    """
    Get the prior complete weeks of daily observations.

    Returns one row per date, Monday through Sunday.
    """
    dates = previous_complete_weekdays(
        anchor_date=anchor_date,
        weeks=lookback_weeks,
    )

    values = daily_counts[category].reindex(dates, fill_value=0)

    return pd.DataFrame(
        {
            "date": dates,
            "day_of_week": dates.dayofweek,
            "day_name": dates.day_name(),
            "count": values.to_numpy(),
        }
    )


def weighted_weekday_forecast(
    daily_counts: pd.DataFrame,
    forecast_dates: pd.DatetimeIndex,
    category: str,
    lookback_weeks: int,
    week_weights: list[float],
    conditions: pd.DataFrame | None = None,
    condition_adjustments: dict[str, float] | None = None,
) -> pd.DataFrame:
    """
    Forecast each date using a weighted average of previous matching weekdays.

    Condition adjustments are explicit assumptions. For example, +0.20 means
    increase the baseline by 20% when that condition is active.
    """
    if len(week_weights) != lookback_weeks:
        raise ValueError(
            "week_weights must contain exactly LOOKBACK_WEEKS values."
        )

    if not any(weight > 0 for weight in week_weights):
        raise ValueError("At least one week weight must be positive.")

    condition_adjustments = condition_adjustments or {}
    conditions = conditions if conditions is not None else pd.DataFrame()

    output = []

    for forecast_date in forecast_dates:
        history_dates = [
            forecast_date - pd.Timedelta(days=7 * offset)
            for offset in range(lookback_weeks, 0, -1)
        ]

        history_values = (
            daily_counts[category]
            .reindex(history_dates, fill_value=0)
            .astype(float)
            .to_numpy()
        )

        weights = np.asarray(week_weights, dtype=float)
        baseline = float(np.average(history_values, weights=weights))

        active_conditions = {}
        adjustment_factor = 1.0

        if forecast_date in conditions.index:
            condition_row = conditions.loc[forecast_date]

            for condition_name, percentage in condition_adjustments.items():
                if (
                    condition_name in conditions.columns
                    and float(condition_row[condition_name]) == 1.0
                ):
                    active_conditions[condition_name] = 1
                    adjustment_factor += percentage

        # Keep forecasts non-negative and round to a whole ticket.
        forecast_value = max(0, baseline * adjustment_factor)

        output.append(
            {
                "date": forecast_date,
                "category": category,
                "baseline_forecast": baseline,
                "condition_adjustment_factor": adjustment_factor,
                "forecast": int(round(forecast_value)),
                "history_dates": ",".join(
                    date.strftime("%Y-%m-%d") for date in history_dates
                ),
                "active_conditions": ",".join(active_conditions) or "none",
            }
        )

    return pd.DataFrame(output)


def forecast_all_categories(
    daily_counts: pd.DataFrame,
    forecast_dates: pd.DatetimeIndex,
    categories: list[str],
    lookback_weeks: int,
    week_weights: list[float],
    conditions: pd.DataFrame | None = None,
    condition_adjustments: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Forecast all categories, then calculate total daily workload."""
    forecasts = []

    for category in categories:
        forecasts.append(
            weighted_weekday_forecast(
                daily_counts=daily_counts,
                forecast_dates=forecast_dates,
                category=category,
                lookback_weeks=lookback_weeks,
                week_weights=week_weights,
                conditions=conditions,
                condition_adjustments=condition_adjustments,
            )
        )

    result = pd.concat(forecasts, ignore_index=True)

    total = (
        result.groupby("date", as_index=False)["forecast"]
        .sum()
        .rename(columns={"forecast": "forecast"})
    )
    total["category"] = "Total"
    total["baseline_forecast"] = (
        result.groupby("date", as_index=False)["baseline_forecast"]
        .sum()["baseline_forecast"]
    )
    total["condition_adjustment_factor"] = np.nan
    total["history_dates"] = ""
    total["active_conditions"] = (
        result.groupby("date")["active_conditions"]
        .apply(
            lambda values: ", ".join(
                sorted(
                    {
                        name
                        for value in values
                        for name in value.split(", ")
                        if name != "none"
                    }
                )
            )
            or "none"
        )
        .reindex(total["date"])
        .to_numpy()
    )

    return pd.concat([result, total], ignore_index=True)
