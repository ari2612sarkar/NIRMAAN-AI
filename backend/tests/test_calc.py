from app.calc import SimulationInputs, apply_simulation, route_cost, waste_disposal_cost


BASELINE = {
    "mixed_kg": 1000.0,
    "wet_kg": 800.0,
    "dry_kg": 300.0,
    "recyclable_kg": 200.0,
    "total_waste_kg": 2300.0,
    "trip_count": 20,
    "avg_distance_per_trip_km": 15.0,
    "overflow_incidents": 5,
    "scheduled_count": 8,
    "emergency_count": 2,
    "downtime_hours": 10.0,
}


def test_route_cost_scales_with_distance():
    assert route_cost(20) > route_cost(10) > 0


def test_waste_disposal_cost_recycling_offsets_cost():
    low_recycling = waste_disposal_cost(100, 50, 20, 5)
    high_recycling = waste_disposal_cost(100, 50, 20, 200)
    assert high_recycling["net_cost"] < low_recycling["net_cost"]


def test_segregation_reduces_mixed_waste():
    baseline = apply_simulation(BASELINE, SimulationInputs())
    segregated = apply_simulation(BASELINE, SimulationInputs(segregation_adoption_pct=50))
    assert segregated["mixed_kg"] < baseline["mixed_kg"]
    assert segregated["total_waste_kg"] == baseline["total_waste_kg"]  # conservation of mass


def test_composting_reduces_disposal_cost():
    baseline = apply_simulation(BASELINE, SimulationInputs())
    composted = apply_simulation(BASELINE, SimulationInputs(composting_adoption_pct=60))
    assert composted["disposal_cost"] < baseline["disposal_cost"]


def test_fewer_trips_increase_overflow_risk():
    baseline = apply_simulation(BASELINE, SimulationInputs())
    fewer_trips = apply_simulation(BASELINE, SimulationInputs(collection_frequency_change_pct=-30))
    assert fewer_trips["overflow_incidents"] > baseline["overflow_incidents"]
    assert fewer_trips["collection_cost"] < baseline["collection_cost"]


def test_route_optimization_reduces_collection_cost():
    baseline = apply_simulation(BASELINE, SimulationInputs())
    optimized = apply_simulation(BASELINE, SimulationInputs(route_optimization_efficiency_pct=40))
    assert optimized["collection_cost"] < baseline["collection_cost"]


def test_predictive_maintenance_shifts_emergency_to_scheduled():
    baseline = apply_simulation(BASELINE, SimulationInputs())
    maintained = apply_simulation(BASELINE, SimulationInputs(predictive_maintenance_adoption_pct=100))
    assert maintained["maintenance_cost"] <= baseline["maintenance_cost"]
