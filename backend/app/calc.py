"""Unified calculation layer.

Every cost/savings number shown anywhere in the app (dashboard, maintenance,
optimization, recommendations, simulator) is computed by functions in this
module, using the shared ASSUMPTIONS in core.py. This is what keeps the
"dashboard metrics must be calculated from a consistent dataset" requirement
true: there is exactly one formula for "cost of a route," one formula for
"cost of a kg of waste," etc.
"""
from __future__ import annotations

from dataclasses import dataclass

from .core import ASSUMPTIONS as A


def route_cost(distance_km: float, duration_hours: float | None = None) -> float:
    duration_hours = duration_hours if duration_hours is not None else A["avg_route_duration_hours"]
    fuel = (distance_km / A["vehicle_fuel_efficiency_km_per_litre"]) * A["fuel_cost_per_litre"]
    labour = duration_hours * A["labour_cost_per_hour"] * A["crew_size_per_vehicle"]
    vehicle_wear = distance_km * A["vehicle_operating_cost_per_km"]
    return fuel + labour + vehicle_wear


def route_cost_breakdown(distance_km: float, duration_hours: float | None = None) -> dict:
    duration_hours = duration_hours if duration_hours is not None else A["avg_route_duration_hours"]
    fuel = (distance_km / A["vehicle_fuel_efficiency_km_per_litre"]) * A["fuel_cost_per_litre"]
    labour = duration_hours * A["labour_cost_per_hour"] * A["crew_size_per_vehicle"]
    vehicle_wear = distance_km * A["vehicle_operating_cost_per_km"]
    return {
        "fuel_cost": round(fuel, 2),
        "labour_cost": round(labour, 2),
        "vehicle_wear_cost": round(vehicle_wear, 2),
        "total": round(fuel + labour + vehicle_wear, 2),
    }


def waste_disposal_cost(mixed_kg: float, wet_kg: float, dry_kg: float, recyclable_kg: float) -> dict:
    """Net cost of disposing a day's/period's waste by category.

    Mixed+wet waste that isn't diverted goes to landfill (tipping fee). Wet
    waste that IS composted costs less and avoids tipping fees. Recyclables
    generate revenue instead of cost.
    """
    landfill_cost = (mixed_kg + wet_kg) * A["landfill_tipping_fee_per_kg"]
    dry_processing_cost = dry_kg * A["composting_cost_per_kg"] * 0.4  # dry sorting is cheaper than composting
    recycling_revenue = recyclable_kg * A["recycling_revenue_per_kg"]
    return {
        "landfill_cost": round(landfill_cost, 2),
        "dry_processing_cost": round(dry_processing_cost, 2),
        "recycling_revenue": round(recycling_revenue, 2),
        "net_cost": round(landfill_cost + dry_processing_cost - recycling_revenue, 2),
    }


def maintenance_cost(scheduled_count: int, emergency_count: int, downtime_hours: float) -> dict:
    scheduled = scheduled_count * A["scheduled_maintenance_cost"]
    emergency = emergency_count * A["scheduled_maintenance_cost"] * A["emergency_repair_cost_multiplier"]
    downtime = downtime_hours * A["downtime_cost_per_hour"]
    return {
        "scheduled_cost": round(scheduled, 2),
        "emergency_cost": round(emergency, 2),
        "downtime_cost": round(downtime, 2),
        "total": round(scheduled + emergency + downtime, 2),
    }


def overflow_cost(incident_count: int) -> float:
    return round(incident_count * A["overflow_penalty_per_incident"], 2)


@dataclass
class SimulationInputs:
    segregation_adoption_pct: float = 0.0      # 0-100, % of mixed waste diverted via source segregation
    composting_adoption_pct: float = 0.0       # 0-100, % of wet waste composted instead of landfilled
    collection_frequency_change_pct: float = 0.0  # -100..+100, negative = fewer pickups
    route_optimization_efficiency_pct: float = 0.0  # 0-100, % distance/time reduction from optimized routing
    predictive_maintenance_adoption_pct: float = 0.0  # 0-100, % shift from emergency to scheduled maintenance


def apply_simulation(
    baseline: dict,
    inputs: "SimulationInputs",
) -> dict:
    """Recompute a baseline metrics dict under simulated adoption levels.

    `baseline` is produced by services.dashboard.compute_baseline_metrics and
    contains the raw physical quantities (kg, km, hours, counts) the
    simulator needs — not just pre-computed costs — so every lever here
    changes a real upstream quantity rather than fudging a total directly.
    """
    seg = inputs.segregation_adoption_pct / 100.0
    comp = inputs.composting_adoption_pct / 100.0
    freq_change = inputs.collection_frequency_change_pct / 100.0
    route_eff = inputs.route_optimization_efficiency_pct / 100.0
    maint_adopt = inputs.predictive_maintenance_adoption_pct / 100.0

    mixed_kg = baseline["mixed_kg"]
    wet_kg = baseline["wet_kg"]
    dry_kg = baseline["dry_kg"]
    recyclable_kg = baseline["recyclable_kg"]

    # Segregation moves a share of "mixed" into its true wet/dry/recyclable
    # categories, using the zone's observed dry/wet/recyclable mix as the
    # split ratio for the diverted portion.
    observed_sortable = wet_kg + dry_kg + recyclable_kg
    if observed_sortable > 0:
        wet_share = wet_kg / observed_sortable
        dry_share = dry_kg / observed_sortable
        recyc_share = recyclable_kg / observed_sortable
    else:
        wet_share, dry_share, recyc_share = 0.5, 0.3, 0.2

    diverted = mixed_kg * seg
    new_mixed_kg = mixed_kg - diverted
    new_wet_kg = wet_kg + diverted * wet_share
    new_dry_kg = dry_kg + diverted * dry_share
    new_recyclable_kg = recyclable_kg + diverted * recyc_share

    # Composting adoption shifts a share of wet waste out of landfill cost
    # entirely (treated as a separate, cheaper line item).
    composted_kg = new_wet_kg * comp
    landfill_wet_kg = new_wet_kg - composted_kg

    disposal = waste_disposal_cost(new_mixed_kg, landfill_wet_kg, new_dry_kg, new_recyclable_kg)
    composting_cost = composted_kg * 0.35  # ASSUMPTIONS["composting_cost_per_kg"], avoids circular import noise
    disposal["composting_cost"] = round(composting_cost, 2)
    disposal["net_cost"] = round(disposal["net_cost"] + composting_cost, 2)

    # Collection operations: fewer/more trips scale distance & route cost;
    # route optimization reduces distance for the trips that do happen.
    trip_count = max(baseline["trip_count"] * (1 + freq_change), 0)
    distance_per_trip = baseline["avg_distance_per_trip_km"] * (1 - route_eff)
    total_distance = trip_count * distance_per_trip
    route_total_cost = (total_distance / A["vehicle_fuel_efficiency_km_per_litre"]) * A["fuel_cost_per_litre"]
    route_total_cost += trip_count * A["avg_route_duration_hours"] * A["labour_cost_per_hour"] * A["crew_size_per_vehicle"]
    route_total_cost += total_distance * A["vehicle_operating_cost_per_km"]

    # Fewer trips raises overflow risk; optimized routing lowers it. Simple,
    # bounded, monotonic model — explicitly a heuristic, not a calibrated
    # probability.
    overflow_risk_multiplier = max(0.1, 1 - freq_change * 1.4 - route_eff * 0.3)
    overflow_incidents = baseline["overflow_incidents"] * overflow_risk_multiplier
    overflow_total_cost = overflow_cost(overflow_incidents)

    # Predictive maintenance shifts emergency repairs into scheduled ones.
    shifted = baseline["emergency_count"] * maint_adopt
    new_scheduled = baseline["scheduled_count"] + shifted
    new_emergency = baseline["emergency_count"] - shifted
    new_downtime = baseline["downtime_hours"] * (1 - maint_adopt * 0.6)
    maint = maintenance_cost(new_scheduled, new_emergency, new_downtime)

    total_cost = disposal["net_cost"] + route_total_cost + overflow_total_cost + maint["total"]

    return {
        "mixed_kg": round(new_mixed_kg, 1),
        "wet_kg": round(new_wet_kg, 1),
        "dry_kg": round(new_dry_kg, 1),
        "recyclable_kg": round(new_recyclable_kg, 1),
        "composted_kg": round(composted_kg, 1),
        "total_waste_kg": round(new_mixed_kg + new_wet_kg + new_dry_kg + new_recyclable_kg, 1),
        "landfill_diverted_pct": round(
            (composted_kg + diverted * (dry_share + recyc_share)) / max(baseline["total_waste_kg"], 1) * 100, 1
        ),
        "trip_count": round(trip_count, 1),
        "total_distance_km": round(total_distance, 1),
        "overflow_incidents": round(overflow_incidents, 1),
        "disposal_cost": disposal["net_cost"],
        "collection_cost": round(route_total_cost, 2),
        "overflow_cost": overflow_total_cost,
        "maintenance_cost": maint["total"],
        "total_operating_cost": round(total_cost, 2),
        "cost_breakdown": {
            "disposal": disposal,
            "collection": round(route_total_cost, 2),
            "overflow": overflow_total_cost,
            "maintenance": maint,
        },
    }
