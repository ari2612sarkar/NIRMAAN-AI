"""App-wide settings, DB engine/session, and cost/operational assumptions.

All cost and physical-unit assumptions live here so every module (forecast,
maintenance, optimization, recommendations, simulator) uses the exact same
numbers. Numbers are realistic-order-of-magnitude Indian municipal waste
operations figures, clearly documented as assumptions (not measured values).
"""
from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR / 'nirmaan.db'}")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Cost & operational assumptions (₹ INR). Documented, not hidden. These are
# the single source of truth for every cost calculation in the app.
# ---------------------------------------------------------------------------
ASSUMPTIONS = {
    "fuel_cost_per_litre": 96.0,            # ₹/litre diesel, Oct 2026 approx.
    "vehicle_fuel_efficiency_km_per_litre": 4.5,
    "labour_cost_per_hour": 55.0,           # ₹/hour per crew member
    "crew_size_per_vehicle": 3,
    "avg_route_duration_hours": 5.0,
    "vehicle_operating_cost_per_km": 18.0,  # tyres, upkeep, depreciation
    "scheduled_maintenance_cost": 3500.0,   # ₹ per scheduled service
    "emergency_repair_cost_multiplier": 3.2,  # emergency vs scheduled
    "downtime_cost_per_hour": 450.0,        # lost productivity per vehicle-hour
    "landfill_tipping_fee_per_kg": 1.1,     # ₹/kg sent to landfill
    "composting_cost_per_kg": 0.35,         # ₹/kg processed via composting
    "recycling_revenue_per_kg": 2.0,        # ₹/kg recovered value from recyclables
    "overflow_penalty_per_incident": 800.0,  # service-complaint / re-dispatch cost
    "segregation_campaign_cost_per_zone": 15000.0,  # one-time implementation cost
    "composting_setup_cost_per_zone": 35000.0,
    "commercial_program_cost_per_zone": 20000.0,
}
