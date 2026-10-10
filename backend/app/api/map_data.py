from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models as m
from .. import services
from ..core import get_db

router = APIRouter(prefix="/api/map", tags=["map"])


@router.get("/bins")
def map_bins(db: Session = Depends(get_db)):
    rows = (
        db.query(m.Bin, m.Location, m.Zone)
        .join(m.Location, m.Bin.location_id == m.Location.id)
        .join(m.Zone, m.Location.zone_id == m.Zone.id)
        .all()
    )
    high_risk_codes = {b["bin_code"] for b in services.high_risk_bins(db, limit=200)}
    return [
        {
            "bin_code": b.bin_code,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "waste_category": b.waste_category,
            "zone_name": z.name,
            "location_name": loc.name,
            "status": b.status,
            "overflow_risk": b.bin_code in high_risk_codes,
        }
        for b, loc, z in rows
    ]


@router.get("/zones")
def map_zones(db: Session = Depends(get_db)):
    rows = db.query(m.Location, m.Zone).join(m.Zone, m.Location.zone_id == m.Zone.id).all()
    out = []
    for loc, z in rows:
        out.append(
            {
                "zone_id": z.id,
                "zone_name": z.name,
                "zone_type": z.zone_type,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
            }
        )
    return out
