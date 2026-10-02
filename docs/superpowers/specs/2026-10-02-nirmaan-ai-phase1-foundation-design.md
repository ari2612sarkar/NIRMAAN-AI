# NIRMAAN AI — Phase 1: Foundation & Architecture

Status: Approved for planning
Date: 2026-10-02

## 1. Context

NIRMAAN AI is a hackathon submission for "Hackathon to Solve India's Garbage
Problem — Technology for a Cleaner Bharat": an AI-first Waste Intelligence &
Cost Optimization Platform that closes the loop
**Predict → Prevent → Optimize → Maintain → Reduce** across municipal waste
operations (generation forecasting, collection routing, predictive
maintenance, cost optimization, waste-reduction interventions, and
what-if simulation), with a grounded AI copilot and role-based dashboards.

The full product (see original request) spans roughly ten subsystems and
22 deliverables — too large for one spec/plan cycle. It has been decomposed
into five sequential phases, each with its own design → spec → plan →
implementation cycle:

1. **Phase 1 — Foundation & Architecture** (this document)
2. Phase 2 — Core AI/ML & Optimization Engines (forecasting, anomaly
   detection, route optimization, predictive maintenance, cost engine,
   waste-reduction recommender)
3. Phase 3 — Simulation, Multi-Agent Orchestration & Copilot
4. Phase 4 — Frontend (dashboards, map, simulator UI, copilot UI, demo mode)
5. Phase 5 — Integration, Testing, Deployment & Deliverables

Decisions already locked in during brainstorming (apply to all phases unless
a later phase's design overrides them):

- No external LLM API — the AI Copilot is rule-based/templated, grounded in
  computed data via explicit tool-call functions (no hallucination risk, no
  API-key dependency, no offline-demo risk).
- Map UI uses Leaflet + OpenStreetMap (no paid API key required).
- Real JWT-based auth with self-registration, plus pre-seeded demo accounts
  per role.
- Real deployment is required eventually (Vercel frontend, Render/Railway
  backend + Postgres) but is deferred to Phase 5; Phases 1-4 target a fully
  working local setup.
- Synthetic dataset targets the spec's maximum scale (200 locations, 500
  bins/assets, 30 vehicles, 12+ months of daily history) and must be clearly
  labeled synthetic everywhere it's surfaced.

## 2. Goals (Phase 1)

- A running FastAPI backend and a running Next.js frontend, talking to each
  other, with nothing faked.
- A complete relational schema for the whole product (all 15 entities from
  the product spec), migrated via Alembic, running on SQLite locally with a
  trivial swap to Postgres for deployment.
- Working registration + login (JWT), with 4 roles, plus pre-seeded demo
  accounts for each role.
- A deterministic synthetic-data generator producing a full year of
  realistic, internally-consistent operational history at the target scale,
  fast enough to re-run during development.
- Deployment scaffolding (Dockerfile, docker-compose, render.yaml, vercel.json,
  .env.example) committed but not yet exercised against real hosting
  accounts.
- Pytest coverage proving the schema, auth flow, and seed script are correct.

## 3. Non-goals (explicitly deferred to later phases)

- Any ML model, forecasting, anomaly detection, optimization, or
  recommendation logic (Phase 2).
- Scenario simulator, multi-agent orchestration, AI copilot (Phase 3).
- Any dashboard/map/chart UI beyond a bare login/register page proving the
  auth flow works end-to-end (Phase 4).
- Actually deploying to Vercel/Render/Postgres-hosted, CI, or writing the
  final README/demo script/write-up deliverables (Phase 5).

## 4. Repo layout & tech stack

```
GarbageAI/
  backend/
    app/
      api/            # FastAPI routers
      models/          # SQLAlchemy ORM models
      schemas/          # Pydantic request/response schemas
      services/          # business logic (auth service, etc.)
      ml/                # (empty scaffold; Phase 2)
      optimization/       # (empty scaffold; Phase 2)
      simulation/          # (empty scaffold; Phase 3)
      core/               # settings, security/JWT, db session
      utils/
    alembic/
    scripts/
      seed_data.py        # synthetic data generator
    tests/
    requirements.txt
    Dockerfile
    .env.example
  frontend/
    app/                  # Next.js App Router
    components/
    lib/
    package.json
    vercel.json
  docker-compose.yml
  render.yaml
  .gitignore
  README.md
  docs/superpowers/specs/
```

Backend: Python 3.11+, FastAPI, SQLAlchemy 2.0 (declarative models),
Pydantic v2, Alembic, `python-jose` (JWT), `passlib[bcrypt]`, `faker`,
`numpy`, `pandas`, `pytest`, `httpx` (test client). Dependency management via
plain `venv` + `requirements.txt` — no Poetry/uv, to minimize setup friction
on the Windows dev machine.

Frontend: Next.js 14 (App Router), TypeScript, Tailwind CSS, plain `npm`.
Phase 1 frontend scope is limited to a login/register page and an
authenticated placeholder landing page, proving the auth contract end to
end; the full dashboard UI is Phase 4.

## 5. Data model

All tables use an integer primary key `id` and, where relevant, a
`created_at`/`updated_at` timestamp. Foreign keys are named `<entity>_id`.

- **users**: email (unique), hashed_password, full_name, role (enum:
  `municipal_admin`, `operations_manager`, `maintenance_manager`,
  `sustainability_manager`), created_at.
- **zones**: name, zone_type (residential/commercial/institutional/mixed),
  population_estimate, description.
- **locations**: zone_id, name, location_type (household/commercial/
  institutional/public), latitude, longitude, address.
- **bins**: location_id, bin_code (unique), capacity_litres, waste_category
  (mixed/wet/dry/recyclable), install_date, sensor_enabled (bool),
  last_known_fill_pct, status (active/maintenance/retired).
- **vehicles**: vehicle_code (unique), vehicle_type (compactor/tipper/etc.),
  capacity_kg, fuel_type, purchase_date, odometer_km, status.
- **assets**: a generic non-bin, non-vehicle infrastructure record
  (compactor, sorting machine, charging equipment, IoT gateway) —
  zone_id, asset_type, install_date, status.
- **waste_records**: location_id, date, waste_category, quantity_kg,
  source (residential/commercial/institutional), notes.
- **collection_events**: bin_id, vehicle_id, route_id (nullable),
  scheduled_at, collected_at (nullable = missed), fill_pct_at_collection,
  quantity_kg.
- **routes**: vehicle_id, date, planned_distance_km, actual_distance_km
  (nullable), planned_duration_min, status (planned/completed/optimized),
  is_optimized (bool).
- **route_stops**: route_id, bin_id, sequence_order, eta, actual_arrival
  (nullable).
- **maintenance_records**: asset_type (bin/vehicle/asset — polymorphic via a
  string discriminator + target id columns), target_id, event_type
  (scheduled/emergency/inspection), cost, downtime_hours, description, date.
- **cost_records**: date, zone_id (nullable for org-wide costs),
  cost_category (fuel/labour/maintenance/infrastructure), amount.
- **interventions**: zone_id, intervention_type (composting/segregation/
  recycling_collection/commercial_program/etc.), proposed_date, status
  (proposed/active/completed), implementation_cost, description.
- **predictions**: prediction_type (waste_forecast/overflow_risk/
  maintenance_risk/anomaly), target_type, target_id, predicted_at,
  predicted_value (JSON), confidence, explanation (JSON) — written by
  Phase 2 services; schema only in Phase 1.
- **recommendations**: recommendation_type, zone_id, generated_at,
  impact_score, expected_waste_reduction_pct, expected_cost_saving,
  implementation_cost, confidence, drivers (JSON), status — written by
  Phase 2/3; schema only in Phase 1.
- **scenarios**: name, created_by (user_id), parameters (JSON), created_at —
  written by Phase 3; schema only in Phase 1.
- **simulation_results**: scenario_id, metric_name, baseline_value,
  simulated_value, unit — written by Phase 3; schema only in Phase 1.
- **data_provenance**: a single-row (or few-row) marker table recording that
  the seeded operational data is synthetic, the generator version/seed used,
  and the generation timestamp — surfaced in the UI/README so synthetic data
  is never mistaken for real municipal data.

Phase 1 implements and seeds: users, zones, locations, bins, vehicles,
assets, waste_records, collection_events, routes, route_stops,
maintenance_records, cost_records, data_provenance. It creates the tables
(via Alembic migration) but does not seed rows for interventions,
predictions, recommendations, scenarios, simulation_results — those remain
empty until Phases 2/3 populate them at runtime.

## 6. Auth design

- Password hashing: bcrypt via `passlib`.
- Tokens: JWT access token (`python-jose`), 7-day expiry, signed with a
  secret from `.env` (`SECRET_KEY`). No refresh token — out of scope for a
  demo-length session.
- Endpoints: `POST /auth/register` (email, password, full_name, role),
  `POST /auth/login` (OAuth2 password flow, returns bearer token),
  `GET /auth/me` (current user from token).
- `get_current_user` FastAPI dependency decodes the bearer token and loads
  the user; a `require_role(*roles)` dependency factory is provided for
  endpoints that need role gating in later phases.
- Seed script also creates 4 demo accounts, one per role, with a fixed,
  documented password (e.g. `Demo@1234`), printed to console and recorded in
  the README so judges can log in immediately without registering.

## 7. Synthetic data generator

`backend/scripts/seed_data.py`, run via `python -m scripts.seed_data` (or a
`make seed` / npm-equivalent convenience command). Design:

- Deterministic: a fixed `--seed` (default 42) drives `random`/`numpy`/
  `Faker` so the dataset is reproducible across machines and re-runs.
- Scale: ~12 zones, 200 locations, 500 bins/assets (bins + other asset
  types combined), 30 vehicles, 365 days of daily history ending "today."
- Realism, not randomness: waste generation has weekday/weekend effects,
  mild seasonal trend, a handful of injected anomalous spikes (so Phase 2's
  anomaly detector has real signal), and a slow year-long upward trend in
  segregation rate for a subset of zones (so Phase 2/3 interventions have
  something real to measure against). Vehicle/asset maintenance history
  includes a few assets with a clear degrading pattern (rising mileage,
  more frequent service events) so Phase 2's predictive-maintenance model
  has genuine failure signal to learn from, and several that are healthy
  throughout, so the model isn't trivially "everything fails."
- Performance: data is built in-memory with numpy/pandas then written with
  chunked bulk inserts (`Session.bulk_insert_mappings` or
  `executemany`-style chunking), targeting well under a minute to generate
  roughly 1M rows on SQLite on a normal laptop.
- Idempotent: running the script drops and recreates the seeded tables
  (not the schema itself) so it can be re-run safely during development.
- Writes one `data_provenance` row recording seed value, generator version,
  and generation timestamp.

## 8. Deployment scaffolding (config only)

- `backend/Dockerfile`: standard Python slim image, installs
  `requirements.txt`, runs `uvicorn`.
- `docker-compose.yml` at repo root: `backend`, `frontend`, and `postgres`
  services for local parity testing (optional path — SQLite remains the
  default local dev DB; compose is there for when Phase 5 wants to rehearse
  Postgres before deploying).
- `render.yaml`: stub web-service definition for the backend plus a managed
  Postgres instance, to be filled in/validated in Phase 5.
- `frontend/vercel.json`: minimal Next.js config stub.
- `.env.example` at repo root (or per-package) listing: `DATABASE_URL`,
  `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `NEXT_PUBLIC_API_BASE_URL`.

None of this is exercised against real hosting accounts in Phase 1 — that's
Phase 5. It exists now so the schema/settings are designed with that swap in
mind from day one (e.g., `DATABASE_URL`-driven engine creation rather than a
hardcoded SQLite path).

## 9. Testing plan (Phase 1)

Pytest, using a throwaway SQLite test database (or in-memory SQLite) and
FastAPI's `TestClient`/`httpx`:

- Model layer: creating one of each entity and its required relationships
  round-trips correctly; foreign-key constraints are enforced.
- Auth: register → login → `/auth/me` happy path; duplicate-email
  rejection; wrong-password rejection; invalid/expired-token rejection;
  role is persisted and returned correctly.
- Seed script: after running with a fixed seed, row counts match expected
  ranges for each seeded table, every foreign key resolves (no orphaned
  bins/vehicles/records), and `data_provenance` has exactly the expected
  row.

## 10. Risks / open questions carried into later phases

- Exact feature set available to the Phase 2 forecasting/maintenance models
  depends on what signal Phase 1's generator actually encodes — Phase 2's
  design will need to inspect the generated data before finalizing feature
  engineering.
- Polymorphic `maintenance_records.target_id` (bin vs vehicle vs asset) is a
  deliberate simplification over three separate FK columns; if this proves
  awkward for SQLAlchemy relationship loading in practice, Phase 2 may
  revisit it — flagged here rather than over-engineered now.
