from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import services
from ..calc import SimulationInputs, apply_simulation
from ..core import get_db
from ..recommendations import top_recommendations

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    baseline = services.compute_baseline_metrics(db, window_days=30)
    current = apply_simulation(baseline, SimulationInputs())

    # "Potential savings" preview: a realistic combined-adoption scenario,
    # same formulas the interactive simulator uses.
    optimized = apply_simulation(
        baseline,
        SimulationInputs(
            segregation_adoption_pct=35,
            composting_adoption_pct=40,
            route_optimization_efficiency_pct=15,
            predictive_maintenance_adoption_pct=50,
        ),
    )
    potential_monthly_saving = round(current["total_operating_cost"] - optimized["total_operating_cost"], 2)

    high_risk_bins = services.high_risk_bins(db, limit=100)
    recs = top_recommendations(db, limit=5)

    return {
        "data_window": {"start": baseline["window_start"], "end": baseline["window_end"]},
        "total_waste_kg_30d": current["total_waste_kg"],
        "operating_cost_30d": current["total_operating_cost"],
        "cost_breakdown": current["cost_breakdown"],
        "overflow_incidents_30d": current["overflow_incidents"],
        "high_risk_bin_count": len(high_risk_bins),
        "landfill_diverted_pct": current["landfill_diverted_pct"],
        "potential_monthly_saving": potential_monthly_saving,
        "top_recommendations": recs,
        "priority_actions": [
            {
                "title": r["title"],
                "impact_score": r["impact_score"],
                "expected_monthly_saving": r["expected_monthly_saving"],
            }
            for r in recs
        ],
    }


@router.get("/zones")
def zones(db: Session = Depends(get_db)):
    return services.zone_summaries(db)


@router.get("/waste-trend")
def waste_trend(zone_id: int | None = None, days: int = 90, db: Session = Depends(get_db)):
    df = services.zone_daily_totals(db, zone_id=zone_id)
    if df.empty:
        return []
    if zone_id is None:
        df = df.groupby("date", as_index=False)["quantity_kg"].sum()
    cutoff = services.latest_data_date(db) - dt.timedelta(days=days)
    df = df[df["date"] >= cutoff].sort_values("date")
    return [{"date": str(r["date"]), "quantity_kg": round(float(r["quantity_kg"]), 1)} for _, r in df.iterrows()]
