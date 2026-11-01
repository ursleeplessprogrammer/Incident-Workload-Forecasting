import argparse
from pathlib import Path

import pandas as pd

from src.config import (
    CATEGORIES,
    CONDITION_ADJUSTMENTS,
    CONDITIONS_PATH,
    FORECAST_DAYS,
    LOOKBACK_WEEKS,
    OUTPUT_DIR,
    TICKET_ID_COLUMN,
    TICKETS_PATH,
    TIMESTAMP_COLUMN,
    CATEGORY_COLUMN,
    TIMEZONE,
    WEEK_WEIGHTS,
)
from src.data_loader import load_conditions, load_tickets
from src.features import aggregate_daily_tickets, make_complete_daily_counts
from src.forecasting import forecast_all_categories
from src.reporting import (
    make_historical_comparison,
    save_forecast_chart,
    save_reports,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Forecast incident workload for all seven weekdays."
    )
    parser.add_argument(
        "--tickets",
        type=Path,
        default=TICKETS_PATH,
        help="Path to ticket-level CSV data.",
    )
    parser.add_argument(
        "--conditions",
        type=Path,
        default=CONDITIONS_PATH,
        help="Optional date-level conditions CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory for generated reports.",
    )
    parser.add_argument(
        "--anchor-date",
        type=str,
        default=None,
        help="Forecast origin date, YYYY-MM-DD. Defaults to latest ticket date.",
    )
    parser.add_argument(
        "--forecast-days",
        type=int,
        default=FORECAST_DAYS,
        help="Number of calendar days to forecast.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    tickets = load_tickets(
        path=args.tickets,
        timestamp_column=TIMESTAMP_COLUMN,
        category_column=CATEGORY_COLUMN,
        timezone=TIMEZONE,
    )

    if TICKET_ID_COLUMN in tickets.columns:
        duplicate_count = int(tickets[TICKET_ID_COLUMN].duplicated().sum())
        if duplicate_count:
            print(f"Warning: dropping {duplicate_count} duplicate ticket IDs.")
            tickets = tickets.drop_duplicates(
                subset=[TICKET_ID_COLUMN],
                keep="first",
            )

    unknown_categories = sorted(
        set(tickets[CATEGORY_COLUMN].dropna().unique()) - set(CATEGORIES)
    )

    if unknown_categories:
        print(
            "Warning: ignoring categories not listed in config.py: "
            f"{unknown_categories}"
        )
        tickets = tickets[tickets[CATEGORY_COLUMN].isin(CATEGORIES)]

    if tickets.empty:
        raise ValueError("No tickets remain after category filtering.")

    daily_counts = aggregate_daily_tickets(
        tickets=tickets,
        timestamp_column=TIMESTAMP_COLUMN,
        category_column=CATEGORY_COLUMN,
        categories=CATEGORIES,
    )

    anchor_date = (
        pd.Timestamp(args.anchor_date).normalize()
        if args.anchor_date
        else daily_counts.index.max().normalize()
    )

    # Historical comparisons only use dates through the selected anchor.
    historical_data = daily_counts.loc[daily_counts.index <= anchor_date]

    if historical_data.empty:
        raise ValueError("No historical ticket data exists on or before anchor date.")

    # This fills absent dates with zero. Confirm data collection was complete.
    historical_data = make_complete_daily_counts(
        historical_data,
        end_date=anchor_date,
    )

    conditions = load_conditions(
        path=args.conditions,
        timezone=TIMEZONE,
    )

    forecast_dates = pd.date_range(
        start=anchor_date + pd.Timedelta(days=1),
        periods=args.forecast_days,
        freq="D",
        name="date",
    )

    forecasts = forecast_all_categories(
        daily_counts=historical_data,
        forecast_dates=forecast_dates,
        categories=CATEGORIES,
        lookback_weeks=LOOKBACK_WEEKS,
        week_weights=WEEK_WEIGHTS,
        conditions=conditions,
        condition_adjustments=CONDITION_ADJUSTMENTS,
    )

    history_comparison = make_historical_comparison(
        daily_counts=historical_data,
        anchor_date=anchor_date,
        categories=CATEGORIES,
        lookback_weeks=LOOKBACK_WEEKS,
    )

    save_reports(
        history_comparison=history_comparison,
        forecasts=forecasts,
        output_dir=args.output,
    )

    chart_history = history_comparison.rename(
        columns={"date": "date"}
    )

    save_forecast_chart(
        history=chart_history,
        forecasts=forecasts,
        output_path=args.output / "workload_forecast.png",
    )

    print(f"\nForecast origin: {anchor_date.date()}")
    print(f"Forecast dates: {forecast_dates[0].date()} to {forecast_dates[-1].date()}")
    print(f"Reports saved in: {args.output.resolve()}")
    print("\nDaily forecast:")
    print(
        forecasts[
            ["date", "category", "baseline_forecast", "forecast", "active_conditions"]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
