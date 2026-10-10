"""Query/aggregation services shared by the API routers.

This is the one place that turns raw ORM rows into the metrics dicts that
calc.py, forecast.py, maintenance.py, and the recommendation engine all
consume — keeping "every number on the dashboard comes from the same
dataset" true in practice, not just in intent.
"""
from __future__ import annotations

import datetime as dt

import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from . import models as m
from .optimization.routes import optimize_route


def latest_data_date(db: Session) -> dt.date:
    result = db.query(func.max(m.WasteRecord.date)).scalar()
    return result or dt.date.today()


def zone_daily_totals(db: Session, zone_id: int | None = None) -> pd.DataFrame:
    q = db.query(m.WasteRecord.date, m.WasteRecord.zone_id, m.WasteRecord.quantity_kg)
    if zone_id is not None:
        q = q.filter(m.WasteRecord.zone_id == zone_id)
    rows = q.all()
    df = pd.DataFrame(rows, columns=["date", "zone_id", "quantity_kg"])
    if df.empty:
        return df
    return df.groupby(["zone_id", "date"], as_index=False)["quantity_kg"].sum()


def category_totals(db: Session, zone_id: int | None, start: dt.date, end: dt.date) -> dict:
    q = db.query(m.WasteRecord.waste_category, func.sum(m.WasteRecord.quantity_kg)).filter(
        m.WasteRecord.date >= start, m.WasteRecord.date <= end
    )
    if zone_id is not None:
        q = q.filter(m.WasteRecord.zone_id == zone_id)
    rows = dict(q.group_by(m.WasteRecord.waste_category).all())
    return {
        "mixed_kg": float(rows.get("mixed", 0.0)),
        "wet_kg": float(rows.get("wet", 0.0)),
        "dry_kg": float(rows.get("dry", 0.0)),
        "recyclable_kg": float(rows.get("recyclable", 0.0)),
    }


def compute_baseline_metrics(db: Session, zone_id: int | None = None, window_days: int = 30) -> dict:
    """Baseline physical-quantity metrics for the last `window_days`, the
    input every simulator/recommendation calculation starts from.
    """
    end = latest_data_date(db)
    start = end - dt.timedelta(days=window_days - 1)

    cats = category_totals(db, zone_id, start, end)
    total_waste_kg = sum(cats.values())

    ce_q = db.query(m.CollectionEvent).join(m.Bin).filter(m.CollectionEvent.date >= start, m.CollectionEvent.date <= end)
    if zone_id is not None:
        ce_q = ce_q.join(m.Location, m.Bin.location_id == m.Location.id).filter(m.Location.zone_id == zone_id)
    events = ce_q.all()
    overflow_incidents = sum(1 for e in events if e.fill_pct_at_collection > 100 or e.missed)
    # A "trip" is one vehicle visiting a zone on a given day and collecting
    # several bins along one route — not one trip per bin. Counting
    # distinct (vehicle, date) pairs avoids wildly overcounting routes.
    trip_count = len({(e.vehicle_id, e.date) for e in events}) or 1

    # Rough average distance per trip: derive from the zone's location spread
    # rather than inventing a constant. Falls back to a sane default.
    locs_q = db.query(m.Location.latitude, m.Location.longitude)
    if zone_id is not None:
        locs_q = locs_q.filter(m.Location.zone_id == zone_id)
    locs = locs_q.all()
    if len(locs) >= 2:
        lats = [l[0] for l in locs]
        lons = [l[1] for l in locs]
        spread_km = max((max(lats) - min(lats)) * 111, (max(lons) - min(lons)) * 111, 1.0)
        avg_distance_per_trip_km = spread_km * 1.6
    else:
        avg_distance_per_trip_km = 12.0

    mr_q = db.query(m.MaintenanceRecord).filter(m.MaintenanceRecord.date >= start, m.MaintenanceRecord.date <= end)
    maint_records = mr_q.all()
    scheduled_count = sum(1 for r in maint_records if r.event_type == "scheduled")
    emergency_count = sum(1 for r in maint_records if r.event_type == "emergency")
    downtime_hours = sum(r.downtime_hours for r in maint_records)

    return {
        "window_start": str(start),
        "window_end": str(end),
        "mixed_kg": cats["mixed_kg"],
        "wet_kg": cats["wet_kg"],
        "dry_kg": cats["dry_kg"],
        "recyclable_kg": cats["recyclable_kg"],
        "total_waste_kg": total_waste_kg,
        "trip_count": trip_count,
        "avg_distance_per_trip_km": round(avg_distance_per_trip_km, 2),
        "overflow_incidents": overflow_incidents,
        "scheduled_count": scheduled_count,
        "emergency_count": emergency_count,
        "downtime_hours": round(downtime_hours, 1),
    }


def high_risk_bins(db: Session, limit: int = 20) -> list[dict]:
    end = latest_data_date(db)
    start = end - dt.timedelta(days=45)
    rows = (
        db.query(m.CollectionEvent, m.Bin, m.Location)
        .join(m.Bin, m.CollectionEvent.bin_id == m.Bin.id)
        .join(m.Location, m.Bin.location_id == m.Location.id)
        .filter(m.CollectionEvent.date >= start)
        .all()
    )
    by_bin: dict[int, list] = {}
    meta: dict[int, tuple] = {}
    for ce, b, loc in rows:
        by_bin.setdefault(b.id, []).append(ce)
        meta[b.id] = (b, loc)

    results = []
    for bin_id, events in by_bin.items():
        events = sorted(events, key=lambda e: e.date)[-5:]
        avg_fill = sum(e.fill_pct_at_collection for e in events) / len(events)
        missed_rate = sum(1 for e in events if e.missed) / len(events)
        risk_score = min(avg_fill * 0.7 + missed_rate * 100 * 0.3, 150)
        if risk_score < 70:
            continue
        b, loc = meta[bin_id]
        results.append(
            {
                "bin_code": b.bin_code,
                "location_name": loc.name,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "waste_category": b.waste_category,
                "avg_fill_pct_last5": round(avg_fill, 1),
                "missed_rate_last5": round(missed_rate, 2),
                "risk_score": round(risk_score, 1),
                "explanation": (
                    f"Averaged {avg_fill:.0f}% full at last {len(events)} collections"
                    + (f", missed {missed_rate:.0%} of recent scheduled pickups" if missed_rate > 0 else "")
                    + "."
                ),
            }
        )
    results.sort(key=lambda r: r["risk_score"], reverse=True)
    return results[:limit]


def zone_summaries(db: Session) -> list[dict]:
    end = latest_data_date(db)
    start = end - dt.timedelta(days=30)
    zones = db.query(m.Zone).all()
    out = []
    for z in zones:
        cats = category_totals(db, z.id, start, end)
        total = sum(cats.values())
        segregation_pct = (cats["dry_kg"] + cats["recyclable_kg"]) / total * 100 if total else 0.0
        out.append(
            {
                "zone_id": z.id,
                "name": z.name,
                "zone_type": z.zone_type,
                "population_estimate": z.population_estimate,
                "total_waste_kg_30d": round(total, 1),
                "segregation_pct": round(segregation_pct, 1),
                **{k: round(v, 1) for k, v in cats.items()},
            }
        )
    return out


def route_optimization_for_zone(db: Session, zone_id: int) -> dict:
    bins = (
        db.query(m.Bin, m.Location)
        .join(m.Location, m.Bin.location_id == m.Location.id)
        .filter(m.Location.zone_id == zone_id)
        .limit(25)
        .all()
    )
    if not bins:
        return {"error": "No bins found for this zone."}
    stops = [
        {"bin_code": b.bin_code, "latitude": loc.latitude, "longitude": loc.longitude}
        for b, loc in bins
    ]
    depot = (stops[0]["latitude"], stops[0]["longitude"])
    result = optimize_route(stops, depot)

    from .calc import route_cost_breakdown

    baseline_cost = route_cost_breakdown(result["baseline_distance_km"])
    optimized_cost = route_cost_breakdown(result["optimized_distance_km"])
    result["baseline_cost"] = baseline_cost
    result["optimized_cost"] = optimized_cost
    result["cost_saved"] = round(baseline_cost["total"] - optimized_cost["total"], 2)
    return result
