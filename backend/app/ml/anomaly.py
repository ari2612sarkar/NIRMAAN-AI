"""Waste-generation anomaly detection via rolling z-score.

Deliberately a transparent statistical method rather than a black-box
model: every flagged day comes with the exact rolling mean/std it was
compared against, which is what "explainable" has to mean in a system a
municipal operator will actually act on.
"""
from __future__ import annotations

import pandas as pd

Z_THRESHOLD = 2.0
WINDOW = 14


def detect_anomalies(daily_totals: pd.DataFrame, zone_name: str) -> list[dict]:
    """daily_totals: DataFrame with columns ['date', 'quantity_kg'] for one zone."""
    df = daily_totals.sort_values("date").reset_index(drop=True)
    if len(df) < WINDOW + 1:
        return []

    df["rolling_mean"] = df["quantity_kg"].rolling(WINDOW, min_periods=WINDOW).mean().shift(1)
    df["rolling_std"] = df["quantity_kg"].rolling(WINDOW, min_periods=WINDOW).std().shift(1)
    df = df.dropna(subset=["rolling_mean", "rolling_std"])
    # A near-zero rolling std (e.g. a perfectly steady history) would blow up
    # the z-score on any real-world rounding noise; floor it relative to the
    # mean so a flat-then-spike pattern still gets caught sanely.
    std_floor = (df["rolling_mean"].abs() * 0.03).clip(lower=0.5)
    df["rolling_std"] = df["rolling_std"].clip(lower=std_floor)
    df["z_score"] = (df["quantity_kg"] - df["rolling_mean"]) / df["rolling_std"]

    flagged = df[df["z_score"].abs() >= Z_THRESHOLD].copy()
    results = []
    for _, row in flagged.iterrows():
        direction = "spike" if row["z_score"] > 0 else "drop"
        pct_vs_avg = (row["quantity_kg"] / row["rolling_mean"] - 1) * 100
        results.append(
            {
                "zone": zone_name,
                "date": str(row["date"]),
                "quantity_kg": round(float(row["quantity_kg"]), 1),
                "rolling_avg_kg": round(float(row["rolling_mean"]), 1),
                "z_score": round(float(row["z_score"]), 2),
                "direction": direction,
                "explanation": (
                    f"{abs(pct_vs_avg):.0f}% {'above' if pct_vs_avg > 0 else 'below'} the "
                    f"{WINDOW}-day rolling average ({row['rolling_mean']:.0f} kg), "
                    f"z-score {row['z_score']:.2f}."
                ),
            }
        )
    # Most extreme first, cap to a sane number for the UI.
    results.sort(key=lambda r: abs(r["z_score"]), reverse=True)
    return results[:25]
