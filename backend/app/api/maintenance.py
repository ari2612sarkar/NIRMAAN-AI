from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models as m
from ..core import get_db
from ..ml.maintenance import score_vehicle

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


@router.get("/risk")
def maintenance_risk(db: Session = Depends(get_db)):
    vehicles = db.query(m.Vehicle).all()
    if not vehicles:
        return []
    fleet_avg_odometer = sum(v.odometer_km for v in vehicles) / len(vehicles)
    as_of = db.query(m.MaintenanceRecord.date).order_by(m.MaintenanceRecord.date.desc()).first()
    as_of_date = as_of[0] if as_of else dt.date.today()

    results = []
    for v in vehicles:
        records = (
            db.query(m.MaintenanceRecord)
            .filter(m.MaintenanceRecord.vehicle_id == v.id)
            .order_by(m.MaintenanceRecord.date)
            .all()
        )
        record_dicts = [
            {"date": r.date, "event_type": r.event_type, "cost": r.cost, "downtime_hours": r.downtime_hours}
            for r in records
        ]
        vehicle_dict = {"vehicle_code": v.vehicle_code, "odometer_km": v.odometer_km}
        score = score_vehicle(vehicle_dict, record_dicts, fleet_avg_odometer, as_of_date)
        score["vehicle_type"] = v.vehicle_type
        score["odometer_km"] = v.odometer_km
        results.append(score)

    results.sort(key=lambda r: r["risk_score"], reverse=True)
    return results


@router.get("/high-risk-bins")
def high_risk_bins(db: Session = Depends(get_db)):
    from .. import services

    return services.high_risk_bins(db, limit=50)
