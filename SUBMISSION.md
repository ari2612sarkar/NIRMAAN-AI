# Hackathon Submission — NIRMAAN AI

## Project title

**NIRMAAN AI — Waste Intelligence & Cost Optimization Platform**

## One-line description

An AI operations platform that forecasts waste generation, optimizes
collection routes, prioritizes vehicle maintenance, recommends costed
waste-reduction interventions, and lets a municipal operator simulate the
combined financial impact of all four before implementing anything.

## Problem statement

Municipal waste management in India is overwhelmingly reactive: fixed
collection schedules regardless of actual demand, maintenance performed
after breakdown rather than before, and no systematic link between
"waste generation is rising" and "here is a specific, costed action to
reduce it." This drives up fuel, labour, and emergency-repair cost while
leaving waste-reduction opportunities (segregation, composting,
commercial-specific collection) largely unquantified and unacted on.

## Solution

NIRMAAN AI treats the waste lifecycle as one connected system rather than
disconnected dashboard widgets. It (1) forecasts near-term waste
generation per zone with a trained ML model, (2) flags abnormal
generation and overflow-risk bins with transparent, explainable scoring,
(3) compares baseline vs. optimized collection routes with real
distance/₹ numbers, (4) scores vehicle maintenance risk and recommends
action before failure, (5) generates costed, ranked waste-reduction
interventions per zone with a documented Impact Score, and (6) lets the
user interactively simulate any combination of these levers and see the
projected effect on total operating cost immediately. A rule-based AI
Copilot exposes all of this conversationally, grounded strictly in the
same computed data — it cannot invent a number the backend didn't
actually calculate.

## Functional AI/ML components

- **Waste forecasting**: `scikit-learn` `RandomForestRegressor`, trained
  per zone on day-of-week, month, trend, 7-day lag, and population
  features; 80% confidence interval from out-of-sample residual spread;
  feature-importance-based explanation. Falls back to a labelled average
  when a zone has under 21 days of history.
- **Anomaly detection**: rolling 14-day z-score per zone (|z| ≥ 2),
  reported with the exact rolling average it was compared against.
- **Predictive maintenance**: a weighted, documented 0–100 risk score
  (mileage vs. fleet average, days overdue for service, recent emergency-
  repair frequency, downtime trend) — explicitly presented as a
  transparent heuristic, not a calibrated failure probability.
- **Route optimization**: nearest-neighbor heuristic over haversine
  distances, compared against the naive baseline stop order, with real
  fuel/labour/vehicle-wear cost deltas.
- **Recommendation engine**: rules-based, zone-conditioned intervention
  generator (segregation / composting / commercial program) that runs
  the *same* simulation function the interactive simulator uses, so a
  recommendation's claimed saving and the simulator's live output can
  never diverge.

## How the product works

A FastAPI backend holds a synthetic-but-realistic year of operational
history (10 zones, 60 locations, 150 bins, 15 vehicles) in SQLite. A
single calculation module (`app/calc.py`) turns any combination of
"adoption levers" into a full cost/waste projection using documented
formulas and shared cost assumptions. Every API endpoint — dashboard,
forecast, maintenance, route optimization, recommendations, the
simulator, and the copilot — reads from or calls into that same module,
so the numbers shown anywhere in the UI are mutually consistent by
construction, not by convention. The Next.js frontend is a single
operations-dashboard page assembling KPIs, charts, a map, a maintenance
table, a route comparison, the recommendation panel, the interactive
simulator, and the copilot chat.

## Impact measurement methodology

Every recommendation and every simulator output is computed, not
guessed: a baseline (do-nothing) run of `apply_simulation` is compared
against a run with the proposed/selected adoption levels, using the same
physical-quantity formulas (₹/km fuel+labour+wear for collection, ₹/kg
landfill/composting/recycling for disposal, ₹/incident for overflow,
scheduled-vs-emergency-repair cost multiples for maintenance). The
"Impact Score" shown for each recommendation is a documented, visible
formula (expected waste reduction % + monthly saving/₹1000 + feasibility
− implementation cost/₹1000 − operational risk), not a hidden ranking.

## Synthetic-data disclosure

**All data in this submission is synthetic**, generated deterministically
(fixed seed) by `backend/scripts/seed_data.py`. No real municipal
records, sensor data, or personal information were used or accessed. The
generator is documented in the README and marked in-app via a
`data_provenance` database record. Cost assumptions (fuel price, labour
rate, tipping fees, etc.) are order-of-magnitude estimates for Indian
municipal operations, not figures sourced from a specific contract.

## Known limitations

- Route optimization uses straight-line distances, not real road routing.
- Maintenance risk is a transparent heuristic score, not a statistically
  validated failure-probability model.
- The AI Copilot is rule-based (deliberately, for demo reliability), not
  an LLM.
- No authentication or multi-tenancy — single-instance demo.
- All financial figures are projected/simulated, not measured real-world
  outcomes — clearly labelled as such throughout the UI.

## Credible pilot plan

1. Deploy to one ward/zone of a willing municipal body, connected to
   their actual bin and vehicle data instead of the synthetic generator.
2. Run collection as normal for 4-6 weeks while the platform's forecasts/
   recommendations are generated but not yet acted on, to validate model
   accuracy against real outcomes.
3. Implement the single highest-impact-score recommendation for that
   zone and measure actual vs. simulator-projected saving.
4. Recalibrate cost assumptions and risk-scoring weights against the
   observed data before expanding to additional zones.
5. Add real road-routing (OSRM) and authentication once there's a
   concrete multi-user, multi-zone rollout to support.

## Tools, frameworks, models, APIs, data sources

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2,
  scikit-learn, pandas, numpy, Faker (dev-time only, for synthetic data
  generation realism), pytest.
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS v4,
  Recharts, Leaflet / react-leaflet, OpenStreetMap tiles (via CARTO dark
  basemap).
- **Database**: SQLite (local demo); schema designed for a trivial
  PostgreSQL swap.
- **No external AI/LLM API** was used — the AI Copilot is fully
  rule-based and grounded in locally computed data.
- **No external/government datasets** were used — all data is synthetic,
  as disclosed above.
