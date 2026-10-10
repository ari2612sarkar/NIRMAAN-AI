"""Collection route optimization: baseline vs. nearest-neighbor heuristic.

Honesty note: this computes straight-line (haversine) distances between
stops, not real road routing (no routing-engine/OSRM dependency for a
2-hour build). It is explicitly labelled as an estimated-distance
heuristic everywhere it's surfaced, per the "don't claim real road
routes" requirement.
"""
from __future__ import annotations

import math


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def route_distance(stops: list[dict], depot: tuple[float, float]) -> float:
    """stops: list of {'latitude', 'longitude', ...} in visiting order."""
    if not stops:
        return 0.0
    total = haversine_km(depot[0], depot[1], stops[0]["latitude"], stops[0]["longitude"])
    for a, b in zip(stops, stops[1:]):
        total += haversine_km(a["latitude"], a["longitude"], b["latitude"], b["longitude"])
    total += haversine_km(stops[-1]["latitude"], stops[-1]["longitude"], depot[0], depot[1])
    return total


def nearest_neighbor_route(stops: list[dict], depot: tuple[float, float]) -> list[dict]:
    remaining = stops.copy()
    route = []
    current = depot
    while remaining:
        nearest = min(
            remaining,
            key=lambda s: haversine_km(current[0], current[1], s["latitude"], s["longitude"]),
        )
        route.append(nearest)
        current = (nearest["latitude"], nearest["longitude"])
        remaining.remove(nearest)
    return route


def optimize_route(baseline_order_stops: list[dict], depot: tuple[float, float]) -> dict:
    """Compares the given (baseline) stop order against a nearest-neighbor
    re-ordering of the same stops, from the same depot.
    """
    baseline_distance = route_distance(baseline_order_stops, depot)
    optimized_stops = nearest_neighbor_route(baseline_order_stops, depot)
    optimized_distance = route_distance(optimized_stops, depot)

    distance_saved = max(baseline_distance - optimized_distance, 0.0)
    pct_saved = (distance_saved / baseline_distance * 100) if baseline_distance > 0 else 0.0

    return {
        "stop_count": len(baseline_order_stops),
        "baseline_distance_km": round(baseline_distance, 2),
        "optimized_distance_km": round(optimized_distance, 2),
        "distance_saved_km": round(distance_saved, 2),
        "pct_distance_saved": round(pct_saved, 1),
        "optimized_stop_order": [s.get("bin_code") or s.get("id") for s in optimized_stops],
        "method": "nearest_neighbor_heuristic_haversine_distance",
        "disclaimer": "Estimated straight-line distances, not real road routing.",
    }
