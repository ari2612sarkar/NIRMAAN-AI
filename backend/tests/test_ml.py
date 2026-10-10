import datetime as dt

import pandas as pd

from app.ml.anomaly import detect_anomalies
from app.ml.forecast import forecast_zone_waste
from app.ml.maintenance import score_vehicle


def _flat_history(days: int, value: float = 100.0, start: dt.date = dt.date(2026, 1, 1)) -> pd.DataFrame:
    return pd.DataFrame(
        {"date": [start + dt.timedelta(days=i) for i in range(days)], "quantity_kg": [value] * days}
    )


def test_forecast_falls_back_with_little_history():
    df = _flat_history(5)
    result = forecast_zone_waste(df, population=10000, horizon_days=3)
    assert result["method"] == "insufficient_history_average_fallback"
    assert len(result["predictions"]) == 3


def test_forecast_trained_model_with_full_history():
    df = _flat_history(60)
    result = forecast_zone_waste(df, population=10000, horizon_days=7)
    assert result["method"] == "random_forest"
    assert len(result["predictions"]) == 7
    for p in result["predictions"]:
        assert p["lower_kg"] <= p["predicted_kg"] <= p["upper_kg"]


def test_anomaly_detects_injected_spike():
    df = _flat_history(40)
    df.loc[35, "quantity_kg"] = 1000.0  # obvious spike
    anomalies = detect_anomalies(df, zone_name="Test Zone")
    assert any(a["date"] == str(df.loc[35, "date"]) for a in anomalies)


def test_maintenance_score_higher_for_degrading_vehicle():
    as_of = dt.date(2026, 10, 1)
    healthy = score_vehicle(
        {"vehicle_code": "V-OK", "odometer_km": 40000},
        [{"date": dt.date(2026, 9, 1), "event_type": "scheduled", "cost": 3500, "downtime_hours": 3}],
        fleet_avg_odometer=50000,
        as_of=as_of,
    )
    degrading = score_vehicle(
        {"vehicle_code": "V-BAD", "odometer_km": 90000},
        [
            {"date": dt.date(2026, 5, 1), "event_type": "scheduled", "cost": 3500, "downtime_hours": 3},
            {"date": dt.date(2026, 7, 1), "event_type": "emergency", "cost": 11000, "downtime_hours": 20},
            {"date": dt.date(2026, 8, 15), "event_type": "emergency", "cost": 11000, "downtime_hours": 30},
            {"date": dt.date(2026, 9, 20), "event_type": "emergency", "cost": 11000, "downtime_hours": 36},
        ],
        fleet_avg_odometer=50000,
        as_of=as_of,
    )
    assert degrading["risk_score"] > healthy["risk_score"]
    assert degrading["risk_level"] in ("medium", "high")
