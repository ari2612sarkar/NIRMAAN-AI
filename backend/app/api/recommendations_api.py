from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import services
from ..core import get_db
from ..recommendations import recommendations_for_zone, top_recommendations

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("")
def all_recommendations(limit: int = 10, db: Session = Depends(get_db)):
    return top_recommendations(db, limit=limit)


@router.get("/zone/{zone_id}")
def zone_recommendations(zone_id: int, db: Session = Depends(get_db)):
    zones = {z["zone_id"]: z for z in services.zone_summaries(db)}
    meta = zones.get(zone_id)
    if not meta:
        return []
    return recommendations_for_zone(db, zone_id, {"name": meta["name"], "zone_type": meta["zone_type"]})
