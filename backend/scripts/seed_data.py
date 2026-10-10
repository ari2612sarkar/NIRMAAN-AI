"""Deterministic synthetic data generator for NIRMAAN AI.

Generates ~1 year of internally-consistent, clearly-labelled-synthetic
municipal waste operations data: zones, locations, bins, vehicles, daily
waste generation, bin collection events, vehicle maintenance history.

Design choices that matter for the ML/optimization modules downstream:
  - Weekday/weekend and seasonal effects in waste generation (forecasting
    needs real signal to find).
  - A handful of injected anomalous spikes, flagged `is_anomalous_seed`
    (anomaly detector can be sanity-checked against ground truth).
  - A rising segregation trend in a subset of "progressive" zones (gives
    the recommendation engine something real to point at).
  - A subset of vehicles with a genuine degrading maintenance pattern
    (rising mileage + more frequent/emergency service) versus healthy
    vehicles that stay reliable all year (predictive maintenance needs
    both classes to be meaningful, not just noise).

Run: `python -m scripts.seed_data` from backend/ with the venv active.
Idempotent: drops and recreates all tables before writing.
"""
from __future__ import annotations

import datetime as dt
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core import Base, engine, SessionLocal  # noqa: E402
from app import models as m  # noqa: E402

SEED = 42
GENERATOR_VERSION = "1.0.0"
N_ZONES = 10
N_LOCATIONS = 60
N_BINS = 150
N_VEHICLES = 15
N_DAYS = 365

random.seed(SEED)
np.random.seed(SEED)

ZONE_TYPES = ["residential", "commercial", "institutional", "mixed"]
LOCATION_TYPE_BY_ZONE = {
    "residential": ["household", "household", "household", "public"],
    "commercial": ["commercial", "commercial", "public"],
    "institutional": ["institutional", "institutional", "public"],
    "mixed": ["household", "commercial", "institutional", "public"],
}
BASE_LAT, BASE_LON = 22.5726, 88.3639  # Kolkata-ish, for a plausible Indian city map

TODAY = dt.date(2026, 10, 10)
START_DATE = TODAY - dt.timedelta(days=N_DAYS - 1)


def chunked_insert(conn, table, rows: list[dict], chunk_size: int = 2000) -> None:
    for i in range(0, len(rows), chunk_size):
        conn.execute(table.insert(), rows[i : i + chunk_size])


def build_zones() -> list[dict]:
    zones = []
    for i in range(N_ZONES):
        zone_type = ZONE_TYPES[i % len(ZONE_TYPES)]
        zones.append(
            {
                "id": i + 1,
                "name": f"Zone {i + 1} ({zone_type.title()})",
                "zone_type": zone_type,
                "population_estimate": int(np.random.randint(8_000, 60_000)),
            }
        )
    return zones


def build_locations(zones: list[dict]) -> list[dict]:
    locations = []
    loc_id = 1
    per_zone = N_LOCATIONS // N_ZONES
    for zone in zones:
        types = LOCATION_TYPE_BY_ZONE[zone["zone_type"]]
        for j in range(per_zone):
            loc_type = types[j % len(types)]
            lat = BASE_LAT + np.random.uniform(-0.12, 0.12)
            lon = BASE_LON + np.random.uniform(-0.12, 0.12)
            locations.append(
                {
                    "id": loc_id,
                    "zone_id": zone["id"],
                    "name": f"{zone['name']} - {loc_type.title()} Site {j + 1}",
                    "location_type": loc_type,
                    "latitude": round(lat, 6),
                    "longitude": round(lon, 6),
                }
            )
            loc_id += 1
    return locations


BIN_CATEGORY_WEIGHTS = {"mixed": 0.40, "wet": 0.25, "dry": 0.20, "recyclable": 0.15}
CAPACITY_OPTIONS = [120.0, 240.0, 360.0, 660.0, 1100.0]


def build_bins(locations: list[dict]) -> list[dict]:
    bins = []
    bin_id = 1
    categories = list(BIN_CATEGORY_WEIGHTS.keys())
    weights = list(BIN_CATEGORY_WEIGHTS.values())
    # Every location gets at least one bin; remaining bins distributed randomly.
    assignments = [loc["id"] for loc in locations]
    while len(assignments) < N_BINS:
        assignments.append(random.choice(locations)["id"])
    assignments = assignments[:N_BINS]
    for loc_id in assignments:
        bins.append(
            {
                "id": bin_id,
                "location_id": loc_id,
                "bin_code": f"B-{bin_id:04d}",
                "capacity_litres": random.choice(CAPACITY_OPTIONS),
                "waste_category": np.random.choice(categories, p=weights),
                "last_known_fill_pct": round(float(np.random.uniform(5, 60)), 1),
                "status": "active",
            }
        )
        bin_id += 1
    return bins


VEHICLE_TYPES = ["compactor", "tipper", "compactor", "mini_compactor"]


def build_vehicles() -> tuple[list[dict], set[int]]:
    vehicles = []
    degrading_ids: set[int] = set()
    for i in range(N_VEHICLES):
        vid = i + 1
        age_years = np.random.uniform(0.5, 7)
        purchase_date = TODAY - dt.timedelta(days=int(age_years * 365))
        is_degrading = i < 4  # first 4 vehicles are the "at risk" fleet subset
        if is_degrading:
            degrading_ids.add(vid)
        odometer = age_years * np.random.uniform(14_000, 22_000) * (1.3 if is_degrading else 1.0)
        vehicles.append(
            {
                "id": vid,
                "vehicle_code": f"V-{vid:02d}",
                "vehicle_type": VEHICLE_TYPES[i % len(VEHICLE_TYPES)],
                "capacity_kg": float(random.choice([5000, 6500, 8000, 9500])),
                "purchase_date": purchase_date,
                "odometer_km": round(float(odometer), 1),
                "status": "active",
            }
        )
    return vehicles, degrading_ids


# Progressive zones (lower-numbered, by construction above) get a rising
# segregation trend across the year; others stay roughly flat.
PROGRESSIVE_ZONE_IDS = {1, 2, 5}

LOCATION_TYPE_BASE_KG = {
    "household": 28.0,
    "commercial": 65.0,
    "institutional": 90.0,
    "public": 20.0,
}


def seasonal_multiplier(day_idx: int) -> float:
    # Mild festive-season bump (Diwali-ish window) + gentle upward yearly trend.
    month = (START_DATE + dt.timedelta(days=day_idx)).month
    festive = 1.18 if month in (10, 11) else 1.0
    trend = 1.0 + 0.0008 * day_idx  # ~+15% over the year, realistic urban growth
    return festive * trend


def build_waste_records(locations: list[dict]) -> tuple[list[dict], list[tuple[int, int]]]:
    records = []
    rec_id = 1
    anomaly_slots: list[tuple[int, int]] = []  # (location_id, day_idx) chosen for injected spikes

    loc_by_zone: dict[int, list[dict]] = {}
    for loc in locations:
        loc_by_zone.setdefault(loc["zone_id"], []).append(loc)

    # Pick ~20 anomaly slots spread across the year on varied locations.
    anomaly_candidates = random.sample(locations, k=min(20, len(locations)))
    for loc in anomaly_candidates:
        day_idx = random.randint(30, N_DAYS - 10)
        anomaly_slots.append((loc["id"], day_idx))
    anomaly_lookup = set(anomaly_slots)

    for loc in locations:
        base = LOCATION_TYPE_BASE_KG[loc["location_type"]]
        is_progressive = loc["zone_id"] in PROGRESSIVE_ZONE_IDS
        for day_idx in range(N_DAYS):
            date = START_DATE + dt.timedelta(days=day_idx)
            weekday = date.weekday()  # 0=Mon
            if loc["location_type"] == "household":
                dow_mult = 1.25 if weekday >= 5 else 1.0  # more weekend household waste
            elif loc["location_type"] == "commercial":
                dow_mult = 0.55 if weekday >= 5 else 1.1  # commercial quieter on weekends
            else:
                dow_mult = 1.0

            total_kg = base * dow_mult * seasonal_multiplier(day_idx)
            total_kg *= np.random.normal(1.0, 0.08)
            total_kg = max(total_kg, 2.0)

            is_anomaly = (loc["id"], day_idx) in anomaly_lookup
            if is_anomaly:
                total_kg *= np.random.uniform(1.8, 2.6)

            # Segregation mix: progressive zones trend dry/recyclable share up
            # over the year; others stay roughly flat.
            if is_progressive:
                dry_recyc_share = 0.18 + 0.22 * (day_idx / N_DAYS)
            else:
                dry_recyc_share = 0.15 + 0.02 * (day_idx / N_DAYS)
            wet_share = 0.45
            mixed_share = max(1 - wet_share - dry_recyc_share, 0.15)

            mixed_kg = total_kg * mixed_share
            wet_kg = total_kg * wet_share
            dry_kg = total_kg * dry_recyc_share * 0.6
            recyclable_kg = total_kg * dry_recyc_share * 0.4

            for category, qty in (
                ("mixed", mixed_kg),
                ("wet", wet_kg),
                ("dry", dry_kg),
                ("recyclable", recyclable_kg),
            ):
                records.append(
                    {
                        "id": rec_id,
                        "location_id": loc["id"],
                        "zone_id": loc["zone_id"],
                        "date": date,
                        "waste_category": category,
                        "quantity_kg": round(float(qty), 2),
                        "is_anomalous_seed": bool(is_anomaly),
                    }
                )
                rec_id += 1
    return records, anomaly_slots


COLLECTION_INTERVAL_DAYS = {"mixed": 2, "wet": 2, "dry": 5, "recyclable": 6}


def build_collection_events(bins: list[dict], vehicles: list[dict]) -> list[dict]:
    events = []
    event_id = 1
    vehicle_ids = [v["id"] for v in vehicles]
    for b in bins:
        interval = COLLECTION_INTERVAL_DAYS[b["waste_category"]]
        day_idx = random.randint(0, interval - 1)
        while day_idx < N_DAYS:
            date = START_DATE + dt.timedelta(days=day_idx)
            fill_pct = float(np.clip(np.random.normal(78, 18), 25, 135))
            missed = fill_pct > 118 and random.random() < 0.5
            quantity_kg = round(b["capacity_litres"] * 0.5 * min(fill_pct, 100) / 100, 2)  # ~0.5 kg/litre waste density
            events.append(
                {
                    "id": event_id,
                    "bin_id": b["id"],
                    "vehicle_id": random.choice(vehicle_ids),
                    "date": date,
                    "fill_pct_at_collection": round(fill_pct, 1),
                    "quantity_kg": quantity_kg,
                    "missed": missed,
                }
            )
            event_id += 1
            day_idx += interval
    return events


def build_maintenance_records(vehicles: list[dict], degrading_ids: set[int]) -> list[dict]:
    records = []
    rec_id = 1
    for v in vehicles:
        is_degrading = v["id"] in degrading_ids
        day_idx = random.randint(10, 70)
        odometer_base = v["odometer_km"] * 0.4
        while day_idx < N_DAYS:
            progress = day_idx / N_DAYS
            odometer_at_event = odometer_base + v["odometer_km"] * 0.6 * progress
            emergency_chance = (0.08 + 0.35 * progress) if is_degrading else 0.06
            event_type = "emergency" if random.random() < emergency_chance else "scheduled"
            cost = (
                3500 * random.uniform(0.85, 1.25)
                if event_type == "scheduled"
                else 3500 * 3.2 * random.uniform(0.8, 1.3)
            )
            downtime = random.uniform(2, 6) if event_type == "scheduled" else random.uniform(8, 36)
            records.append(
                {
                    "id": rec_id,
                    "vehicle_id": v["id"],
                    "date": START_DATE + dt.timedelta(days=day_idx),
                    "event_type": event_type,
                    "cost": round(cost, 2),
                    "downtime_hours": round(downtime, 1),
                    "odometer_km_at_event": round(odometer_at_event, 1),
                }
            )
            rec_id += 1
            # Degrading vehicles get serviced more often as the year goes on.
            next_gap = int(np.clip(70 - 35 * progress, 20, 70)) if is_degrading else random.randint(55, 85)
            day_idx += next_gap
    return records


def build_cost_records(zones: list[dict], waste_records: list[dict], maintenance_records: list[dict]) -> list[dict]:
    """Aggregate daily per-zone cost line items from the generated activity,
    using the same assumption constants as app.calc, so seeded cost_records
    are consistent with anything calc.py recomputes live.
    """
    from app.core import ASSUMPTIONS as A

    records = []
    rec_id = 1

    # zone x date -> total waste kg (drives collection/disposal cost proxy)
    waste_by_zone_date: dict[tuple[int, dt.date], float] = {}
    for r in waste_records:
        key = (r["zone_id"], r["date"])
        waste_by_zone_date[key] = waste_by_zone_date.get(key, 0.0) + r["quantity_kg"]

    maint_total_by_date: dict[dt.date, float] = {}
    for r in maintenance_records:
        maint_total_by_date[r["date"]] = maint_total_by_date.get(r["date"], 0.0) + r["cost"]

    n_zones = len(zones)
    for (zone_id, date), waste_kg in waste_by_zone_date.items():
        # Rough proxy: assume waste_kg maps to a fraction of a standard route.
        implied_km = waste_kg / 35.0  # ~35kg collected per km of route, order-of-magnitude assumption
        fuel = (implied_km / A["vehicle_fuel_efficiency_km_per_litre"]) * A["fuel_cost_per_litre"]
        labour = (implied_km / 25.0) * A["labour_cost_per_hour"] * A["crew_size_per_vehicle"]
        infra = waste_kg * 0.05

        records.append({"id": rec_id, "date": date, "zone_id": zone_id, "cost_category": "fuel", "amount": round(fuel, 2)})
        rec_id += 1
        records.append({"id": rec_id, "date": date, "zone_id": zone_id, "cost_category": "labour", "amount": round(labour, 2)})
        rec_id += 1
        records.append({"id": rec_id, "date": date, "zone_id": zone_id, "cost_category": "infrastructure", "amount": round(infra, 2)})
        rec_id += 1
        maint_share = maint_total_by_date.get(date, 0.0) / n_zones
        records.append({"id": rec_id, "date": date, "zone_id": zone_id, "cost_category": "maintenance", "amount": round(maint_share, 2)})
        rec_id += 1
    return records


def main() -> None:
    print(f"Seeding NIRMAAN AI synthetic data (seed={SEED}, version={GENERATOR_VERSION})...")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    zones = build_zones()
    locations = build_locations(zones)
    bins = build_bins(locations)
    vehicles, degrading_ids = build_vehicles()
    waste_records, anomaly_slots = build_waste_records(locations)
    collection_events = build_collection_events(bins, vehicles)
    maintenance_records = build_maintenance_records(vehicles, degrading_ids)
    cost_records = build_cost_records(zones, waste_records, maintenance_records)

    with engine.begin() as conn:
        chunked_insert(conn, m.Zone.__table__, zones)
        chunked_insert(conn, m.Location.__table__, locations)
        chunked_insert(conn, m.Bin.__table__, bins)
        chunked_insert(conn, m.Vehicle.__table__, vehicles)
        chunked_insert(conn, m.WasteRecord.__table__, waste_records)
        chunked_insert(conn, m.CollectionEvent.__table__, collection_events)
        chunked_insert(conn, m.MaintenanceRecord.__table__, maintenance_records)
        chunked_insert(conn, m.CostRecord.__table__, cost_records)
        conn.execute(
            m.DataProvenance.__table__.insert(),
            [
                {
                    "id": 1,
                    "seed": SEED,
                    "generator_version": GENERATOR_VERSION,
                    "generated_at": dt.datetime.utcnow(),
                    "note": (
                        "100% synthetic demonstration data generated by "
                        "scripts/seed_data.py. Not real municipal records."
                    ),
                }
            ],
        )

    print(f"  zones: {len(zones)}")
    print(f"  locations: {len(locations)}")
    print(f"  bins: {len(bins)}")
    print(f"  vehicles: {len(vehicles)} ({len(degrading_ids)} seeded as degrading/high-risk)")
    print(f"  waste_records: {len(waste_records)} ({len(anomaly_slots)} injected anomaly days)")
    print(f"  collection_events: {len(collection_events)}")
    print(f"  maintenance_records: {len(maintenance_records)}")
    print(f"  cost_records: {len(cost_records)}")
    print("Done.")


if __name__ == "__main__":
    main()
