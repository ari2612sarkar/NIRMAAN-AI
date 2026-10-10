from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models as m
from .. import services
from ..core import get_db

router = APIRouter(prefix="/api/routes", tags=["routes"])


@router.get("/optimize/{zone_id}")
def optimize(zone_id: int, db: Session = Depends(get_db)):
    zone = db.query(m.Zone).filter(m.Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(404, "Zone not found")
    result = services.route_optimization_for_zone(db, zone_id)
    result["zone_id"] = zone_id
    result["zone_name"] = zone.name
    return result
