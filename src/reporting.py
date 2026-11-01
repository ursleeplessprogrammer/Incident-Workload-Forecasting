from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def make_historical_comparison(
    daily_counts: pd.DataFrame,
    anchor_date: pd.Timestamp,
    categories: list[str],
    lookback_weeks: int,
) -> pd.DataFrame:
    """Create weekday-by-week historical comparison tables."""
    anchor_date = pd.Timestamp(anchor_date).normalize()
    current_monday = anchor_date - pd.Timedelta(days=anchor_date.weekday())

    rows = []

    for days_back in range(lookback_weeks, 0, -1):
        week_start = current_monday - pd.Timedelta(days=7 * days_back)
        week_label = f"{days_back}W Ago"

        for offset in range(7):
            date = week_start + pd.Timedelta(days=offset)

            record = {
                "date": date,
                "week_label": week_label,
                "day_name": date.day_name(),
            }

            for category in categories + ["Total"]:
                record[category] = float(
                    daily_counts[category].get(date, 0)
                )

            rows.append(record)

    return pd.DataFrame(rows)


def save_forecast_chart(
    history: pd.DataFrame,
    forecasts: pd.DataFrame,
    output_path: Path,
    category: str = "Total",
) -> None:
    """Save a chart comparing recent total workload with forecast workload."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    history_total = (
        history.groupby("date", as_index=False)[category]
        .sum()
        .sort_values("date")
    )

    future = (
        forecasts[forecasts["category"] == category]
        .sort_values("date")
    )

    plt.figure(figsize=(12, 5))
    plt.plot(
        history_total["date"],
        history_total[category],
        marker="o",
        label="Historical workload",
    )
    plt.plot(
        future["date"],
        future["forecast"],
        marker="o",
        linestyle="--",
        label="Forecast workload",
    )

    plt.title(f"Daily {category} Workload Forecast")
    plt.xlabel("Date")
    plt.ylabel("Ticket count")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def save_reports(
    history_comparison: pd.DataFrame,
    forecasts: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Write CSV reports."""
    output_dir.mkdir(parents=True, exist_ok=True)

    history_comparison.to_csv(
        output_dir / "historical_week_comparison.csv",
        index=False,
    )
    forecasts.to_csv(
        output_dir / "daily_forecast.csv",
        index=False,
    )
