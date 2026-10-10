from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models as m
from .. import services
from ..core import get_db
from ..ml.anomaly import detect_anomalies
from ..ml.forecast import forecast_zone_waste

router = APIRouter(prefix="/api/forecast", tags=["forecast"])


@router.get("/zone/{zone_id}")
def zone_forecast(zone_id: int, horizon_days: int = 7, db: Session = Depends(get_db)):
    zone = db.query(m.Zone).filter(m.Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(404, "Zone not found")
    df = services.zone_daily_totals(db, zone_id=zone_id)
    if df.empty:
        raise HTTPException(404, "No waste history for this zone")
    result = forecast_zone_waste(df[["date", "quantity_kg"]], zone.population_estimate, horizon_days)
    result["zone_id"] = zone_id
    result["zone_name"] = zone.name
    return result


@router.get("/anomalies")
def anomalies(zone_id: int | None = None, db: Session = Depends(get_db)):
    zones = db.query(m.Zone).all()
    if zone_id is not None:
        zones = [z for z in zones if z.id == zone_id]
    out = []
    for z in zones:
        df = services.zone_daily_totals(db, zone_id=z.id)
        if df.empty:
            continue
        out.extend(detect_anomalies(df[["date", "quantity_kg"]], z.name))
    out.sort(key=lambda r: abs(r["z_score"]), reverse=True)
    return out[:50]
