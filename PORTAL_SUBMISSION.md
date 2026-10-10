# Portal Submission — Copy-Ready Fields

Cross-checked against `SUBMISSION.md` and `SYSTEM_DESIGN.md` for
consistency. No deployed URL or public repository is referenced below
because none exists yet (no git remote is configured, nothing is
deployed) — see `SUBMISSION_CHECKLIST.md` item 6 if the portal requires
one.

---

**Project title:**

NIRMAAN AI — Waste Intelligence & Cost Optimization Platform

**One-line description:**

An AI-powered waste operations platform that forecasts waste
generation, optimizes collection costs, prioritizes maintenance, and
simulates waste-reduction interventions.

**Final description (use if a longer field is available; otherwise use
`SUBMISSION.md` verbatim):**

NIRMAAN AI connects the full municipal waste lifecycle — forecasting,
collection routing, predictive maintenance, cost calculation, and
waste-reduction recommendations — into one system built around a single
shared calculation layer, so every number shown (dashboard,
recommendations, simulator) is produced consistently rather than by
disconnected logic. A trained regression model forecasts per-zone waste
with a confidence interval; a rolling z-score detector flags anomalies
with the exact comparison shown; a nearest-neighbor heuristic compares
baseline vs. optimized collection routes on real distance and cost; a
transparent weighted score prioritizes vehicle maintenance; a
rules-based engine proposes costed interventions per zone with a
documented Impact Score. An interactive simulator lets a user adjust
adoption levers (segregation, composting, route efficiency, predictive
maintenance, collection frequency) and see the projected cost/waste
impact immediately. A rule-based AI Copilot answers questions by
calling the same backend functions directly, with no external LLM
dependency.

**Target users:**

Municipal operations managers, maintenance coordinators, and
sustainability teams working at the ward/zone, campus, or township
level.

**Functional features:**

- Executive dashboard with 30-day waste/cost KPIs and ranked AI
  priority actions.
- Per-zone waste forecasting with confidence intervals and feature
  explanations.
- Rolling-window anomaly detection with explicit comparisons.
- Baseline-vs-optimized collection route comparison (distance and cost).
- Explainable vehicle maintenance risk scoring with recommended actions.
- Costed, ranked waste-reduction recommendations with a documented
  Impact Score, expected saving, implementation cost, and payback
  period.
- Interactive what-if simulator across five adoption levers.
- Operations map (Leaflet/OpenStreetMap) with overflow-risk highlighting.
- Rule-based AI Copilot grounded in live computed data.

**AI/ML methodology:**

- Waste forecasting: `scikit-learn` `RandomForestRegressor`, trained
  per zone per request on day-of-week/month/trend/7-day-lag/population
  features, with an 80% confidence interval from out-of-sample residual
  spread, and a documented average fallback under 21 days of history.
- Anomaly detection: rolling 14-day z-score per zone (|z| ≥ 2).
- Predictive maintenance: a documented weighted heuristic (mileage,
  service-overdue status, emergency-repair frequency, downtime trend) —
  explicitly not a calibrated failure-probability classifier.
- Route optimization: nearest-neighbor heuristic over haversine
  (straight-line) distances vs. a naive baseline order.
- Recommendation engine: rules-based intervention generator scored by a
  documented Impact Score formula, using the same simulation function
  the interactive simulator uses.

**Actual tools and libraries used:**

Backend — Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2,
scikit-learn, pandas, numpy, Faker (synthetic data generation), pytest.
Frontend — Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS
v4, Recharts, Leaflet / react-leaflet, OpenStreetMap tiles. Database —
SQLite (local), schema portable to PostgreSQL via `DATABASE_URL`. No
external AI/LLM API is used anywhere in the application.

**Dataset provenance:**

100% synthetic. Generated deterministically (fixed seed 42) by
`backend/scripts/seed_data.py`: 10 zones, 60 locations, 150 bins/assets,
15 vehicles, 365 days of daily history, with injected anomalies, a
rising segregation trend in a subset of zones, and a genuinely
degrading subset of the vehicle fleet. No real municipal records,
sensor data, government datasets, or personal information were used.
Recorded in-database via a `data_provenance` table.

**Measurable evaluation methods:**

- 13/13 backend pytest tests passing (cost/simulation formula
  correctness, forecast fallback vs. trained-model behavior, anomaly
  detection on a known injected spike, maintenance-risk ordering between
  a healthy and a degrading vehicle, route-optimization monotonicity).
- Frontend production build + TypeScript type-check passing cleanly.
- Numerical-consistency checks confirming: fewer collection trips
  increase (not decrease) projected overflow risk; waste mass is
  conserved (not duplicated or lost) under segregation simulation;
  optimized routes are never longer than baseline; the dashboard and the
  simulator's baseline calculation agree exactly (single source of
  truth, not two divergent calculations).
- All ML/optimization outputs ship with their own explanation (feature
  importance, z-score + rolling average, risk-factor breakdown,
  distance/cost delta) rather than being presented as unexplained
  numbers.

**Limitations:**

All data is synthetic — no real deployment or measured outcome exists.
Route distances are estimated (straight-line/haversine), not real road
routing. Maintenance risk is an explainable heuristic, not a
statistically calibrated model. The AI Copilot is rule-based, not an
LLM. No authentication/multi-tenancy — single-instance demo.

**Future pilot plan:**

Deploy against one real municipal zone's actual bin/vehicle data for
several weeks without acting on recommendations, to validate forecast
and risk-score accuracy; then implement the single highest-impact
recommendation for that zone and compare measured outcomes against the
simulator's prior projection before recalibrating assumptions and
expanding to additional zones.

**Public repository / deployment URL:**

Not provided — no git remote is configured and the application is not
deployed. (Decide separately whether to push to GitHub / deploy before
submitting; see `SUBMISSION_CHECKLIST.md`.)
