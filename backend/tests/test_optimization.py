from app.optimization.routes import haversine_km, optimize_route


def test_haversine_known_distance():
    # Kolkata to Delhi is roughly 1300-1500km as the crow flies.
    d = haversine_km(22.5726, 88.3639, 28.7041, 77.1025)
    assert 1300 < d < 1500


def test_optimized_route_never_worse_than_baseline():
    depot = (22.57, 88.36)
    stops = [
        {"bin_code": "B1", "latitude": 22.60, "longitude": 88.40},
        {"bin_code": "B2", "latitude": 22.50, "longitude": 88.30},
        {"bin_code": "B3", "latitude": 22.65, "longitude": 88.45},
        {"bin_code": "B4", "latitude": 22.55, "longitude": 88.32},
    ]
    result = optimize_route(stops, depot)
    assert result["optimized_distance_km"] <= result["baseline_distance_km"]
    assert result["distance_saved_km"] >= 0
    assert len(result["optimized_stop_order"]) == len(stops)
