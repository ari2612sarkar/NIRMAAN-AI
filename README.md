# NIRMAAN AI — Waste Intelligence & Cost Optimization Platform

**Predict → Prevent → Optimize → Maintain → Reduce**

Built for *Hackathon to Solve India's Garbage Problem — Technology for a
Cleaner Bharat*.

## Problem

Municipal waste operations in India are largely reactive: collection
schedules don't track actual demand, maintenance happens after a vehicle
breaks down rather than before, and there's no feedback loop connecting
"how much waste is being generated" to "what can be done to generate
less of it." The result is higher fuel/labour cost, missed pickups and
overflow, emergency repairs instead of planned maintenance, and almost no
visibility into which interventions (segregation, composting, commercial
collection programs) would actually move the numbers.

## Solution

NIRMAAN AI is a single operations platform that closes that loop for a
municipal zone, ward, campus, or township:

1. **Forecast** daily waste generation per zone with a trained regression
   model + confidence interval, and flag anomalous spikes/drops with a
   transparent statistical method.
2. **Prioritize** overflow-risk bins and maintenance-risk vehicles with
   explainable risk scores (not black-box probabilities).
3. **Optimize** collection routes (nearest-neighbor heuristic vs. a naive
   baseline) and show the real distance/fuel/cost difference.
4. **Recommend** concrete, costed waste-reduction interventions (source
   segregation, composting, commercial programs) with a transparent Impact
   Score, expected saving, implementation cost, and payback period.
5. **Simulate** any combination of those levers interactively and see the
   projected effect on waste, distance, overflow, and total operating cost
   immediately — before anything is actually implemented.
6. **Ask** a rule-based AI Copilot grounded entirely in the same computed
   data (cost breakdowns, zone priorities, maintenance risk, what-if
   scenarios) — no external LLM, no hallucinated numbers.

Every number comes from one shared calculation layer
(`backend/app/calc.py`), so the dashboard, the recommendation engine, and
the interactive simulator can never silently disagree with each other.

## Features

- **Executive dashboard**: 30-day waste/cost KPIs, cost breakdown chart,
  overflow and high-risk-bin counts, potential monthly saving, ranked
  "AI Priorities Today" action list.
- **Waste forecasting**: per-zone RandomForest regression with an 80%
  confidence band and feature-importance explanation; falls back to a
  transparent average when a zone has too little history.
- **Anomaly detection**: rolling 14-day z-score per zone, with the exact
  comparison (rolling average, z-score) shown for every flagged day.
- **Predictive maintenance**: a weighted, explainable 0–100 risk score per
  vehicle (mileage, service-overdue, emergency-repair frequency, downtime
  trend) with a recommended action.
- **Collection route optimization**: nearest-neighbor re-ordering vs. the
  original stop order, compared on distance and ₹ cost, with an explicit
  disclaimer that distances are estimated (haversine), not real road
  routing.
- **Waste-reduction recommendation engine**: per-zone interventions with a
  documented Impact Score formula, expected saving, implementation cost,
  payback period, and confidence.
- **Interactive simulator**: five sliders (segregation, composting, route
  efficiency, predictive maintenance adoption, collection frequency)
  recompute baseline-vs-simulated waste/cost/overflow instantly.
- **Operations map**: all bins across all zones (Leaflet + OpenStreetMap),
  colored by category, overflow-risk bins highlighted.
- **AI Copilot**: answers grounded questions (cost breakdown, zone
  priority, maintenance priority, recommendations, segregation what-if)
  by calling the same backend functions as the rest of the UI.

## Architecture

```
GarbageAI/
  backend/            FastAPI + SQLAlchemy + SQLite
    app/
      core.py          DB engine/session + shared cost assumptions
      models.py        ORM schema
      calc.py          unified cost/simulation calculation layer
      services.py      query/aggregation helpers
      recommendations.py   rules-based intervention engine
      ml/
        forecast.py     RandomForestRegressor waste forecasting
        anomaly.py       rolling z-score anomaly detection
        maintenance.py   weighted vehicle risk scoring
      optimization/
        routes.py        haversine distance + nearest-neighbor routing
      api/               FastAPI routers (dashboard, forecast, maintenance,
                          routes, recommendations, simulate, map, copilot)
    scripts/seed_data.py  deterministic synthetic data generator
    tests/                pytest for calc/ml/optimization logic
  frontend/           Next.js (App Router) + TypeScript + Tailwind
    app/page.tsx         single-page operations dashboard
    components/          KPI cards, charts (Recharts), map (react-leaflet),
                          simulator, recommendation panel, copilot chat
    lib/api.ts            typed API client
```

No auth system, multi-agent LLM framework, or Kubernetes/CI setup — cut
deliberately to keep the core workflow (forecast → optimize → maintain →
recommend → simulate) real and fully working end to end within the
hackathon's time budget, per the project's own prioritization rules.

## Tech stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2,
  scikit-learn (RandomForestRegressor), pandas/numpy, pytest.
- **Frontend**: Next.js 16 (App Router), React 19, TypeScript, Tailwind
  CSS v4, Recharts, Leaflet/react-leaflet.
- **Database**: SQLite (file-based, zero setup for local demo/judging).

## Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
python -m scripts.seed_data  # generates ~1 year of synthetic data into nirmaan.db
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

API docs available at `http://127.0.0.1:8000/docs` once running.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`. The frontend expects the backend at
`http://127.0.0.1:8000` by default (`frontend/.env.local`,
`NEXT_PUBLIC_API_BASE_URL`).

## Data provenance

All operational data (zones, locations, bins, vehicles, waste records,
collection events, maintenance records, cost records) is **100% synthetic**,
generated deterministically by `backend/scripts/seed_data.py` (fixed seed
42). It is designed to be internally consistent and to encode realistic
patterns — weekday/weekend effects, seasonal trend, injected anomalies,
a rising segregation trend in a subset of zones, and a genuinely
degrading subset of the vehicle fleet — so the ML/optimization modules
have real signal to work with, not noise. A `data_provenance` table in
the database records the generator version and seed used. No real
municipal records, personal data, or government datasets were used.

## Limitations

- Route optimization uses straight-line (haversine) distances between
  stops, not a real road-routing engine — explicitly disclosed in the UI.
- Predictive maintenance is a transparent weighted risk score, not a
  statistically calibrated failure probability from a trained classifier
  — there isn't enough labelled real-world failure data (synthetic or
  otherwise) in a hackathon-scale dataset to justify presenting it as one.
- The AI Copilot is rule-based (keyword-to-tool-call matching), not an
  LLM — this was a deliberate choice for demo reliability (no API key, no
  hallucination risk, works fully offline) over conversational flexibility.
- No authentication/multi-tenant support — this is a single-instance
  demo, not a production multi-municipality system.
- All cost assumptions (fuel price, labour rate, tipping fees, etc., in
  `backend/app/core.py`) are documented order-of-magnitude estimates for
  Indian municipal operations, not sourced from a specific city's actual
  contracts.

## Future deployment plan

1. Swap SQLite for managed PostgreSQL (schema already uses
   SQLAlchemy/`DATABASE_URL`, no code changes needed).
2. Deploy backend (Docker) to Render/Railway/Fly.io; frontend to Vercel.
3. Replace the synthetic generator with a real ingestion pipeline from a
   municipality's existing bin-sensor/vehicle-telemetry/billing systems.
4. Add authentication and per-zone/per-role access control once there are
   real multi-user stakeholders (operations, maintenance, sustainability
   teams) who need different views.
5. Replace haversine route distances with a real routing engine (OSRM/
   Google Routes API) once road-network data for the pilot city is
   available.
6. Pilot in one ward/zone for one collection cycle, compare actual vs.
   simulator-projected savings, and recalibrate the cost assumptions and
   risk-scoring weights against real outcomes before wider rollout.

See `SUBMISSION.md`, `DEMO_SCRIPT.md`, and `SYSTEM_DESIGN.md` for the
hackathon submission write-up, demo video script, and architecture
walkthrough script respectively.
