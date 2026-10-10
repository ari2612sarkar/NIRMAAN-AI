"""Waste generation forecasting.

A real, trained scikit-learn regression model (RandomForestRegressor),
fit on-demand from the zone's own daily waste history. Features: day of
week, month, a linear trend index, population, and a 7-day lagged
moving average. Confidence interval is derived from the empirical spread
of residuals on held-out recent days, not invented.

Kept deliberately simple (no persisted model file, no MLflow, no
hyperparameter search) — for a dataset this size, retraining in
~100ms on every request is both fast enough and avoids a whole class of
"stale model" bugs during a demo.
"""
from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


def _feature_frame(df: pd.DataFrame, population: int) -> pd.DataFrame:
    df = df.sort_values("date").reset_index(drop=True)
    df["day_of_week"] = df["date"].apply(lambda d: d.weekday())
    df["month"] = df["date"].apply(lambda d: d.month)
    df["day_idx"] = range(len(df))
    df["lag7_avg"] = df["quantity_kg"].rolling(7, min_periods=1).mean().shift(1).bfill()
    df["population"] = population
    return df


FEATURES = ["day_of_week", "month", "day_idx", "lag7_avg", "population"]


def forecast_zone_waste(
    daily_totals: pd.DataFrame,
    population: int,
    horizon_days: int = 7,
) -> dict:
    """daily_totals: DataFrame with columns ['date', 'quantity_kg'], one row
    per day, already aggregated across categories for the zone.
    """
    df = _feature_frame(daily_totals.copy(), population)
    if len(df) < 21:
        # Not enough history for a trustworthy model; fall back to a
        # transparent average-based projection, clearly labelled as such.
        avg = float(df["quantity_kg"].mean()) if len(df) else 0.0
        last_date = df["date"].max() if len(df) else dt.date.today()
        preds = [
            {"date": str(last_date + dt.timedelta(days=i + 1)), "predicted_kg": round(avg, 1),
             "lower_kg": round(avg * 0.85, 1), "upper_kg": round(avg * 1.15, 1)}
            for i in range(horizon_days)
        ]
        return {
            "method": "insufficient_history_average_fallback",
            "predictions": preds,
            "feature_importance": {},
            "explanation": "Fewer than 21 days of history — using a simple average fallback instead of a trained model.",
        }

    X = df[FEATURES].values
    y = df["quantity_kg"].values

    train_cutoff = max(len(df) - 14, int(len(df) * 0.8))
    X_train, y_train = X[:train_cutoff], y[:train_cutoff]
    X_val, y_val = X[train_cutoff:], y[train_cutoff:]

    model = RandomForestRegressor(n_estimators=150, max_depth=8, random_state=42)
    model.fit(X_train, y_train)

    if len(X_val) > 0:
        val_preds = model.predict(X_val)
        residual_std = float(np.std(y_val - val_preds)) if len(y_val) > 1 else float(np.std(y_train)) * 0.3
    else:
        residual_std = float(np.std(y_train)) * 0.3
    residual_std = max(residual_std, 1.0)

    # Refit on full data for the actual forecast (validation split was only
    # to estimate uncertainty honestly).
    model.fit(X, y)

    last_row = df.iloc[-1]
    last_date = last_row["date"]
    rolling_history = list(df["quantity_kg"].tail(7).values)

    preds = []
    day_idx = int(last_row["day_idx"])
    for i in range(horizon_days):
        future_date = last_date + dt.timedelta(days=i + 1)
        day_idx += 1
        lag7_avg = float(np.mean(rolling_history[-7:]))
        feat = np.array([[future_date.weekday(), future_date.month, day_idx, lag7_avg, population]])
        pred = float(model.predict(feat)[0])
        pred = max(pred, 0.0)
        rolling_history.append(pred)
        preds.append(
            {
                "date": str(future_date),
                "predicted_kg": round(pred, 1),
                "lower_kg": round(max(pred - 1.28 * residual_std, 0), 1),  # ~80% interval
                "upper_kg": round(pred + 1.28 * residual_std, 1),
            }
        )

    importances = dict(zip(FEATURES, model.feature_importances_.tolist()))
    top_feature = max(importances, key=importances.get)
    feature_labels = {
        "day_of_week": "day-of-week pattern",
        "month": "seasonal/monthly pattern",
        "day_idx": "overall rising trend",
        "lag7_avg": "recent 7-day average level",
        "population": "zone population",
    }

    return {
        "method": "random_forest",
        "predictions": preds,
        "feature_importance": {k: round(v, 3) for k, v in importances.items()},
        "explanation": (
            f"Forecast driven mainly by {feature_labels.get(top_feature, top_feature)} "
            f"(importance {importances[top_feature]:.0%}); 80% confidence band from "
            f"out-of-sample residual spread (±{residual_std:.1f} kg)."
        ),
    }
