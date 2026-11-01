# 📊 Incident Workload Forecasting

<p align="center">
      <img src="https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
      <img src="https://img.shields.io/badge/IDE-Visual%20Studio%20Code-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white" />
</p>

> Forecast daily workload across email incidents, job batches, and Service Requests—then compare the estimate with recent history and known conditions.

## Overview

This project refactors my Google Apps Script workload-comparison concept into a modular Python application. It counts tickets by category for **every day of the week, Monday through Sunday**, uses the previous four matching weekdays to create a simple forecast, and applies optional adjustments for known conditions such as planned releases or maintenance.

<img width="637" height="509" alt="image" src="https://github.com/user-attachments/assets/f2ef0578-2e50-4f3b-89c4-d1112810e735" />


The project also creates a historical week-comparison report and a chart. Its forecasting method is an explainable baseline, not a validated production model. Forecasts should be compared with actual results before being used for operational planning.

## 🗺️ Contents

- [Project Goals](#-project-goals)
- [How the Forecast Works](#-how-the-forecast-works)
- [Project Structure](#-project-structure)
- [Input Data](#-input-data)
- [Setup](#-setup)
- [Run the Project](#-run-the-project)
- [Output Files](#-output-files)
- [Configuration](#️-configuration)
- [How the Code Is Organized](#-how-the-code-is-organized)
- [Assumptions and Limitations](#️-assumptions-and-limitations)
- [Evaluating the Forecast](#-evaluating-the-forecast)
- [Ideas for Improvement](#-ideas-for-improvement)

## 🎯 Project Goals

The project is designed to:

- Count email incidents, job-batch incidents, and Service Requests separately.
- Include all seven calendar days, including weekends.
- Compare recent ticket counts for matching weekdays.
- Produce a simple forecast for a selected number of future days.
- Apply visible adjustments for conditions known in advance.
- Save reports and a workload chart for review.

## 🔄 How the Forecast Works

The forecast uses a **weighted weekday baseline**. For each forecast date, it finds the same weekday in each of the preceding four weeks, calculates a weighted average, and optionally adjusts it for known conditions.

For example, a Monday forecast uses the counts from the previous four Mondays.

```text
Previous matching weekdays
              ↓
       Weighted average
              ↓
  Apply known condition factors
              ↓
  Forecast for each ticket category
              ↓
        Sum category totals
```

The default configuration gives each of the four weeks equal weight. You can change the weights if you want recent weeks to have more influence.

The forecast is calculated separately for each ticket category. The **Total** forecast is the sum of those category forecasts.

### Known-condition adjustments

Conditions are supplied in `conditions.csv` and configured in `src/config.py`. For example, a planned release can increase the baseline by a configured percentage.

These adjustments are **manual assumptions**, not effects learned from historical data. A `0.20` adjustment means “increase the baseline by 20% when this condition applies”; it does not establish that releases actually cause that increase. Review and validate these values against past outcomes.

## 📁 Project Structure

```text
incident-workload-forecast/
├── data/
│   ├── daily_tickets.csv
│   └── conditions.csv
├── output/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── data_loader.py
│   ├── date_utils.py
│   ├── features.py
│   ├── forecasting.py
│   ├── reporting.py
│   └── main.py
├── requirements.txt
└── README.md
```

- `data/` contains input CSV files.
- `src/` contains the application code, divided by responsibility.
- `output/` is created when reports are generated.
- `requirements.txt` lists the Python libraries needed by the project.
- `README.md` documents the project.

## 📥 Input Data

### `data/daily_tickets.csv`

Despite its filename, this file should contain **one row per ticket**, not pre-aggregated daily totals. The script aggregates ticket rows into daily counts.

Required columns:

| Column | Purpose |
|---|---|
| `created_at` | Ticket creation timestamp |
| `category` | Ticket category |
| `ticket_id` | Optional identifier used to remove duplicate tickets |

Example:

```csv
created_at,category,ticket_id
2025-01-06 09:14:00,Email Incident,INC-001
2025-01-06 10:02:00,Job Batch,INC-002
2025-01-06 11:20:00,Service Request,SER-003
2025-01-07 08:45:00,Email Incident,INC-004
```

The category values must match the names in `CATEGORIES` in `src/config.py`, unless you update that list.

### `data/conditions.csv`

This file is optional. It contains **one row per date** and numeric flags for known conditions.

Example:

```csv
date,planned_release,scheduled_batch,maintenance,public_holiday
2025-01-06,1,0,0,0
2025-01-07,0,1,1,0
2025-01-08,0,0,0,0
```

Use `1` when a condition applies and `0` when it does not. Include only conditions that would have been known when the forecast was created.

## ⚙️ Setup

Use a supported Python 3 version. From the project root, create and activate a virtual environment if desired.

```bash
python -m venv .venv
```

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS or Linux:**

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

`requirements.txt` should contain:

```text
pandas
numpy
matplotlib
```

## ▶️ Run the Project

Run the default forecast from the project root:

```bash
python -m src.main
```

Choose a forecast origin date and horizon:

```bash
python -m src.main --anchor-date 2025-01-31 --forecast-days 7
```

The anchor date is the **forecast origin**. Forecast dates begin on the following day.

You can specify alternate input and output paths:

```bash
python -m src.main \
  --tickets data/daily_tickets.csv \
  --conditions data/conditions.csv \
  --output output \
  --forecast-days 14
```

On Windows Command Prompt, enter the command on one line or use the appropriate line-continuation character.

## 📤 Output Files

The project writes these files to `output/`:

### `daily_forecast.csv`

Contains forecast rows for each date and ticket category, plus a `Total` row.

Important columns include:

| Column | Meaning |
|---|---|
| `date` | Forecast date |
| `category` | Email incident, job batch, Service Request, or Total |
| `baseline_forecast` | Weighted average before condition adjustments |
| `condition_adjustment_factor` | Multiplier applied to the baseline |
| `forecast` | Adjusted, rounded ticket-count estimate |
| `history_dates` | Dates used for the weekday baseline |
| `active_conditions` | Conditions applied to that forecast |

The result is a point estimate; it does not include a statistically calculated prediction interval.

### `historical_week_comparison.csv`

Shows the counts from the previous four complete Monday–Sunday weeks. It provides historical context for the forecast.

### `workload_forecast.png`

A chart comparing recent historical total workload with the forecast total. It is a visual summary, not an additional forecasting model.

## 🛠️ Configuration

Edit `src/config.py` to adapt the project to your data and planning process.

### Input and output paths

```python
TICKETS_PATH = ROOT_DIR / "data" / "daily_tickets.csv"
CONDITIONS_PATH = ROOT_DIR / "data" / "conditions.csv"
OUTPUT_DIR = ROOT_DIR / "output"
```

### Column names and categories

```python
TIMESTAMP_COLUMN = "created_at"
CATEGORY_COLUMN = "category"
TICKET_ID_COLUMN = "ticket_id"

CATEGORIES = [
    "Email Incident",
    "Job Batch",
    "Service Request",
]
```

Change these values if your CSV uses different column names or category labels.

### Time zone

```python
TIMEZONE = "UTC"
```

Set this to the time zone used by the ticket system, such as `"America/New_York"` or `"Europe/London"`. Incorrect time-zone handling can assign tickets to the wrong calendar date.

### Forecast settings

```python
FORECAST_DAYS = 7
LOOKBACK_WEEKS = 4
WEEK_WEIGHTS = [1.0, 1.0, 1.0, 1.0]
```

- `FORECAST_DAYS` sets the number of future dates to forecast.
- `LOOKBACK_WEEKS` sets how many previous matching weekdays to use.
- `WEEK_WEIGHTS` sets the relative weight for each historical week, ordered oldest to newest. It must contain one value per lookback week.

### Condition adjustments

```python
CONDITION_ADJUSTMENTS = {
    "planned_release": 0.20,
    "scheduled_batch": 0.10,
    "maintenance": 0.15,
    "public_holiday": -0.25,
}
```

These values represent percentage adjustments. For example, `0.20` applies a 20% increase. They are assumptions supplied by the project configuration—not relationships inferred by the code.

## 🧩 How the Code Is Organized

### `src/__init__.py`

Marks `src` as a Python package so the project can use imports such as:

```python
from src.config import CATEGORIES
```

It only needs a short docstring or can be empty.

### `src/config.py`

Stores file paths, column names, categories, time-zone settings, forecast settings, and condition adjustments.

### `src/data_loader.py`

Loads the ticket and condition CSV files, checks required columns, parses timestamps, and standardizes timestamps to the configured time zone.

### `src/date_utils.py`

Provides date helpers for complete calendar ranges and prior complete Monday–Sunday weeks.

### `src/features.py`

Aggregates ticket rows into daily category counts, fills missing dates, and creates basic calendar fields.

### `src/forecasting.py`

Calculates the weighted same-weekday baseline, applies configured condition adjustments, and combines category forecasts into a total.

### `src/reporting.py`

Builds a historical comparison table, writes CSV reports, and saves the chart.

### `src/main.py`

Connects the modules: loads inputs, prepares counts, selects the forecast origin, runs the forecast, and saves outputs.

## ⚠️ Assumptions and Limitations

- **The data must be complete for missing dates to mean zero.** The script fills absent dates with zero. If a date is missing because data collection failed, this will understate workload.
- **Categories must match configuration.** Unrecognized categories are ignored after a warning.
- **The forecast is a simple baseline.** It is not a fitted statistical or machine-learning model.
- **Manual condition effects are assumptions.** They need to be checked against historical data.
- **Historical counts do not explain causes.** A difference around a release or holiday does not prove the condition caused it.
- **The current baseline does not model longer-term trends or changing seasonality.**
- **No prediction intervals are calculated.** The output does not quantify forecast uncertainty.
- **No formal historical backtest is included.** Forecast quality must be evaluated before operational use.
- **The chart displays recent comparisons.** It does not independently generate predictions.

## 📏 Evaluating the Forecast

To test whether this baseline is useful, recreate historical forecast situations:

1. Choose a date in the past as the forecast origin.
2. Use only ticket history available on or before that date.
3. Generate forecasts for the following seven or fourteen days.
4. Compare predictions with the actual ticket counts.
5. Repeat for several forecast origins.
6. Summarize errors by category, weekday, and forecast horizon.

Useful metrics include:

- **MAE:** Average absolute difference between forecast and actual count.
- **RMSE:** Gives greater weight to large forecast errors.
- **Bias:** Indicates whether forecasts tend to be too high or too low.

Use a **chronological evaluation**: train or calculate the forecast from earlier dates, then evaluate on later dates. Do not use actual future ticket counts to calculate features for a forecast made in the past. Scikit-learn’s `TimeSeriesSplit` documents a cross-validation approach that avoids training on future observations and evaluating on the past. ([scikit-learn: TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html))

## 🚀 Ideas for Improvement

- Add automated backtesting across multiple historical forecast dates.
- Add forecast-error metrics to the output.
- Compare the baseline with seasonal naïve, exponential-smoothing, or regression models.
- Learn condition effects from historical data instead of setting them manually.
- Add holidays from a maintained calendar source.
- Add separate forecasts by support team or service.
- Add prediction intervals to communicate uncertainty.
- Add data-quality checks for missing dates and unexpected category names.
- Create a dashboard to compare forecasts with actual workload over time.

---
## 📄 License

Please refer to the repository for applicable licensing information.

## 👨‍💻 Author

**ursleeplessprogrammer**

*This project turns historical ticket counts into a transparent starting forecast. Review its assumptions, measure its past performance, and treat its output as planning support—not a guaranteed workload figure.*
