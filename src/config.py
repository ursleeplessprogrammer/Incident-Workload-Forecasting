from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

TICKETS_PATH = ROOT_DIR / "data" / "daily_tickets.csv"
CONDITIONS_PATH = ROOT_DIR / "data" / "conditions.csv"
OUTPUT_DIR = ROOT_DIR / "output"

TIMESTAMP_COLUMN = "created_at"
CATEGORY_COLUMN = "category"
TICKET_ID_COLUMN = "ticket_id"

CATEGORIES = [
    "Email Incident",
    "Job Batch",
    "Service Request",
]

# Use an IANA timezone matching your ticket system.
# Example: "America/New_York", "Europe/London", "UTC"
TIMEZONE = "UTC"

# Forecast the next seven calendar days.
FORECAST_DAYS = 7

# Number of prior same-weekday observations used by the baseline.
LOOKBACK_WEEKS = 4

# Recent matching weekdays receive more weight.
# Four-week history is ordered oldest to newest.
WEEK_WEIGHTS = [1.0, 1.0, 1.0, 1.0]

# Optional adjustments for known conditions.
# These are assumptions, not learned causal effects.
CONDITION_ADJUSTMENTS = {
    "planned_release": 0.20,
    "scheduled_batch": 0.10,
    "maintenance": 0.15,
    "public_holiday": -0.25,
}
