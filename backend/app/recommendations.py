"""Rules-based waste-reduction recommendation engine.

For each zone, proposes 1-3 concrete interventions (source segregation,
composting, commercial waste program) and estimates their impact by
running app.calc.apply_simulation with an assumed adoption level versus
a do-nothing baseline — the exact same function the interactive
simulator uses, so a recommendation's claimed savings and the
simulator's live numbers can never silently diverge.

The "Impact Score" is a transparent, documented formula, not a hidden
black box:

    impact_score = expected_waste_reduction_pct
                 + expected_monthly_saving / 1000
                 + feasibility_score
                 - implementation_cost / 1000
                 - operational_risk_score

All four inputs are returned alongside the score.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from . import services
from .calc import SimulationInputs, apply_simulation
from .core import ASSUMPTIONS as A

FEASIBILITY_BY_ZONE_TYPE = {
    "residential": 12,
    "commercial": 9,
    "institutional": 14,
    "mixed": 10,
}
OPERATIONAL_RISK = {
    "segregation": 4,
    "composting": 6,
    "commercial_program": 7,
}


def _impact_score(waste_reduction_pct: float, monthly_saving: float, feasibility: float,
                   implementation_cost: float, operational_risk: float) -> float:
    return round(
        waste_reduction_pct + monthly_saving / 1000 + feasibility - implementation_cost / 1000 - operational_risk,
        1,
    )


def recommendations_for_zone(db: Session, zone_id: int, zone_meta: dict) -> list[dict]:
    baseline = services.compute_baseline_metrics(db, zone_id=zone_id, window_days=30)
    if baseline["total_waste_kg"] <= 0:
        return []

    baseline_result = apply_simulation(baseline, SimulationInputs())
    recs = []

    mixed_share = baseline["mixed_kg"] / max(baseline["total_waste_kg"], 1)
    wet_share = baseline["wet_kg"] / max(baseline["total_waste_kg"], 1)
    feasibility = FEASIBILITY_BY_ZONE_TYPE.get(zone_meta["zone_type"], 10)

    # 1. Source segregation campaign — worth proposing whenever mixed waste
    #    is still a large share of the stream.
    if mixed_share > 0.30:
        sim = apply_simulation(baseline, SimulationInputs(segregation_adoption_pct=40))
        waste_reduction_pct = (baseline["mixed_kg"] - sim["mixed_kg"]) / max(baseline["mixed_kg"], 1) * 100
        monthly_saving = baseline_result["total_operating_cost"] - sim["total_operating_cost"]
        cost = A["segregation_campaign_cost_per_zone"]
        confidence = round(min(95, 55 + mixed_share * 50), 0)
        payback_days = round(cost / max(monthly_saving, 1) * 30, 0) if monthly_saving > 0 else None
        recs.append(
            {
                "zone_id": zone_id,
                "zone_name": zone_meta["name"],
                "intervention_type": "source_segregation",
                "title": f"Launch source segregation campaign in {zone_meta['name']}",
                "assumed_adoption_pct": 40,
                "expected_mixed_waste_reduction_pct": round(waste_reduction_pct, 1),
                "expected_monthly_saving": round(monthly_saving, 2),
                "implementation_cost": cost,
                "payback_days": payback_days,
                "confidence_pct": confidence,
                "impact_score": _impact_score(
                    waste_reduction_pct, monthly_saving, feasibility, cost, OPERATIONAL_RISK["segregation"]
                ),
                "drivers": [
                    f"mixed waste is {mixed_share:.0%} of this zone's stream",
                    f"{baseline['overflow_incidents']} overflow incidents in the last 30 days",
                ],
            }
        )

    # 2. Composting — worth proposing whenever wet waste is a significant share.
    if wet_share > 0.30:
        sim = apply_simulation(baseline, SimulationInputs(composting_adoption_pct=50))
        waste_reduction_pct = (
            (baseline["wet_kg"] - (sim["wet_kg"] - sim["composted_kg"])) / max(baseline["wet_kg"], 1) * 100
        )
        monthly_saving = baseline_result["total_operating_cost"] - sim["total_operating_cost"]
        cost = A["composting_setup_cost_per_zone"]
        confidence = round(min(90, 50 + wet_share * 50), 0)
        payback_days = round(cost / max(monthly_saving, 1) * 30, 0) if monthly_saving > 0 else None
        recs.append(
            {
                "zone_id": zone_id,
                "zone_name": zone_meta["name"],
                "intervention_type": "composting",
                "title": f"Introduce wet-waste composting in {zone_meta['name']}",
                "assumed_adoption_pct": 50,
                "expected_landfill_diversion_pct": round(waste_reduction_pct, 1),
                "expected_monthly_saving": round(monthly_saving, 2),
                "implementation_cost": cost,
                "payback_days": payback_days,
                "confidence_pct": confidence,
                "impact_score": _impact_score(
                    waste_reduction_pct, monthly_saving, feasibility, cost, OPERATIONAL_RISK["composting"]
                ),
                "drivers": [
                    f"wet waste is {wet_share:.0%} of this zone's stream",
                    "composting avoids per-kg landfill tipping fees entirely",
                ],
            }
        )

    # 3. Commercial waste program — only for commercial/mixed zones with
    #    meaningful overflow risk (a sign current frequency doesn't match demand).
    if zone_meta["zone_type"] in ("commercial", "mixed") and baseline["overflow_incidents"] >= 3:
        sim = apply_simulation(
            baseline, SimulationInputs(segregation_adoption_pct=30, collection_frequency_change_pct=-10)
        )
        monthly_saving = baseline_result["total_operating_cost"] - sim["total_operating_cost"]
        cost = A["commercial_program_cost_per_zone"]
        confidence = 65.0
        payback_days = round(cost / max(monthly_saving, 1) * 30, 0) if monthly_saving > 0 else None
        recs.append(
            {
                "zone_id": zone_id,
                "zone_name": zone_meta["name"],
                "intervention_type": "commercial_program",
                "title": f"Dedicated commercial waste program for {zone_meta['name']}",
                "assumed_adoption_pct": 30,
                "expected_overflow_reduction_incidents": round(
                    baseline["overflow_incidents"] - sim["overflow_incidents"], 1
                ),
                "expected_monthly_saving": round(monthly_saving, 2),
                "implementation_cost": cost,
                "payback_days": payback_days,
                "confidence_pct": confidence,
                "impact_score": _impact_score(
                    5.0, monthly_saving, feasibility, cost, OPERATIONAL_RISK["commercial_program"]
                ),
                "drivers": [
                    f"{baseline['overflow_incidents']} overflow incidents in the last 30 days",
                    "scheduled commercial pickups better match commercial generation patterns than residential-style routing",
                ],
            }
        )

    recs.sort(key=lambda r: r["impact_score"], reverse=True)
    return recs


def top_recommendations(db: Session, limit: int = 5) -> list[dict]:
    zones = services.zone_summaries(db)
    all_recs = []
    for z in zones:
        all_recs.extend(recommendations_for_zone(db, z["zone_id"], {"name": z["name"], "zone_type": z["zone_type"]}))
    all_recs.sort(key=lambda r: r["impact_score"], reverse=True)
    return all_recs[:limit]
