from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import services
from ..calc import SimulationInputs, apply_simulation
from ..core import get_db

router = APIRouter(prefix="/api/simulate", tags=["simulate"])


class SimulateRequest(BaseModel):
    zone_id: int | None = None
    segregation_adoption_pct: float = Field(0, ge=0, le=100)
    composting_adoption_pct: float = Field(0, ge=0, le=100)
    collection_frequency_change_pct: float = Field(0, ge=-100, le=100)
    route_optimization_efficiency_pct: float = Field(0, ge=0, le=100)
    predictive_maintenance_adoption_pct: float = Field(0, ge=0, le=100)


@router.post("")
def run_simulation(req: SimulateRequest, db: Session = Depends(get_db)):
    baseline = services.compute_baseline_metrics(db, zone_id=req.zone_id, window_days=30)
    baseline_result = apply_simulation(baseline, SimulationInputs())
    simulated_result = apply_simulation(
        baseline,
        SimulationInputs(
            segregation_adoption_pct=req.segregation_adoption_pct,
            composting_adoption_pct=req.composting_adoption_pct,
            collection_frequency_change_pct=req.collection_frequency_change_pct,
            route_optimization_efficiency_pct=req.route_optimization_efficiency_pct,
            predictive_maintenance_adoption_pct=req.predictive_maintenance_adoption_pct,
        ),
    )
    savings = round(baseline_result["total_operating_cost"] - simulated_result["total_operating_cost"], 2)
    return {
        "window": {"start": baseline["window_start"], "end": baseline["window_end"]},
        "baseline": baseline_result,
        "simulated": simulated_result,
        "monthly_saving": savings,
        "annual_saving_projection": round(savings * 12, 2),
        "note": "Simulated/projected figures from documented formulas — not measured real-world results.",
    }
