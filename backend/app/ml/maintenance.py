"""Predictive maintenance risk scoring for vehicles.

Explicitly a transparent weighted risk score (0-100), NOT a calibrated
failure probability from a trained classifier — the seed dataset's
"degrading vehicle" pattern is designed to make this score behave
sensibly, but presenting it as a statistically validated probability
would overstate what a few hundred synthetic maintenance events can
actually support. Every score ships with the weighted factors that
produced it.
"""
from __future__ import annotations

import datetime as dt

import numpy as np

WEIGHTS = {
    "mileage": 0.25,
    "service_overdue": 0.30,
    "emergency_frequency": 0.30,
    "downtime_trend": 0.15,
}

EXPECTED_SERVICE_INTERVAL_DAYS = 75


def score_vehicle(
    vehicle: dict,
    maintenance_records: list[dict],
    fleet_avg_odometer: float,
    as_of: dt.date,
) -> dict:
    records = sorted(maintenance_records, key=lambda r: r["date"])
    factors = {}

    # 1. Mileage relative to fleet average (higher = more risk).
    mileage_ratio = vehicle["odometer_km"] / max(fleet_avg_odometer, 1.0)
    mileage_score = float(np.clip((mileage_ratio - 0.7) / 1.0, 0, 1)) * 100
    factors["mileage"] = round(mileage_score, 1)

    # 2. Days since last service vs. expected interval.
    if records:
        last_service_date = records[-1]["date"]
        days_since = (as_of - last_service_date).days
    else:
        days_since = EXPECTED_SERVICE_INTERVAL_DAYS * 2
    overdue_ratio = days_since / EXPECTED_SERVICE_INTERVAL_DAYS
    overdue_score = float(np.clip((overdue_ratio - 0.6) / 1.2, 0, 1)) * 100
    factors["service_overdue"] = round(overdue_score, 1)

    # 3. Emergency repairs in the last 180 days (frequency = real distress signal).
    cutoff = as_of - dt.timedelta(days=180)
    recent = [r for r in records if r["date"] >= cutoff]
    emergency_count = sum(1 for r in recent if r["event_type"] == "emergency")
    emergency_score = float(np.clip(emergency_count / 3.0, 0, 1)) * 100
    factors["emergency_frequency"] = round(emergency_score, 1)

    # 4. Downtime trend: recent downtime vs. earlier downtime.
    if len(records) >= 4:
        midpoint = len(records) // 2
        early_downtime = np.mean([r["downtime_hours"] for r in records[:midpoint]])
        recent_downtime = np.mean([r["downtime_hours"] for r in records[midpoint:]])
        downtime_growth = (recent_downtime - early_downtime) / max(early_downtime, 1.0)
        downtime_score = float(np.clip(downtime_growth, 0, 1.5) / 1.5) * 100
    else:
        downtime_score = 20.0
    factors["downtime_trend"] = round(downtime_score, 1)

    risk_score = sum(factors[k] * WEIGHTS[k] for k in WEIGHTS)
    risk_score = round(float(np.clip(risk_score, 0, 100)), 1)

    if risk_score >= 70:
        level = "high"
    elif risk_score >= 40:
        level = "medium"
    else:
        level = "low"

    driver_labels = {
        "mileage": "mileage well above fleet average",
        "service_overdue": "overdue for scheduled service",
        "emergency_frequency": "repeated recent emergency repairs",
        "downtime_trend": "rising downtime per incident",
    }
    top_drivers = sorted(factors.items(), key=lambda kv: kv[1] * WEIGHTS[kv[0]], reverse=True)
    explanation_drivers = [driver_labels[k] for k, v in top_drivers if v > 35][:3]
    if not explanation_drivers:
        explanation_drivers = ["no strong individual risk factor — score reflects a healthy combined profile"]

    estimated_cost_if_deferred = 3500 * 3.2  # emergency repair vs. scheduled, from shared assumptions
    return {
        "vehicle_code": vehicle["vehicle_code"],
        "risk_score": risk_score,
        "risk_level": level,
        "factors": factors,
        "days_since_last_service": days_since,
        "drivers": explanation_drivers,
        "recommended_action": (
            "Schedule immediate inspection and preventive service"
            if level == "high"
            else "Schedule routine service within the normal interval"
            if level == "medium"
            else "No action needed — continue normal monitoring"
        ),
        "estimated_cost_if_deferred": round(estimated_cost_if_deferred, 2),
    }
