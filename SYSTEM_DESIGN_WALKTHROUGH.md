# NIRMAAN AI — System-Design Walkthrough (60–90s)

Companion to the full `SYSTEM_DESIGN.md`; this is the condensed script
for a short technical walkthrough video, distinct from the product demo
in `DEMO_SCRIPT.md`. This one can be screen-recorded over the codebase
and/or `http://127.0.0.1:8000/docs`, not the dashboard UI.

## Recording checklist

- [ ] Backend running (`uvicorn app.main:app --port 8000`) with seeded
      data, `/docs` reachable.
- [ ] Editor open to: `backend/app/calc.py`, `backend/app/services.py`,
      `backend/app/ml/forecast.py`, `backend/app/optimization/routes.py`,
      `backend/app/recommendations.py`.
- [ ] `SYSTEM_DESIGN.md`'s Mermaid diagram (section 2) rendered/visible
      (any Markdown previewer that supports Mermaid, or paste into
      `https://mermaid.live`).
- [ ] Have the numerical-consistency `curl` checks from `SYSTEM_DESIGN.md`
      §6 ready to re-run live if there's time (optional — not required).

## Narration script

**[0:00–0:15] Architecture**

> "NIRMAAN AI is a two-tier system: a FastAPI backend holding all data
> and computation, and a Next.js frontend that renders it. There's no
> job queue or separate model-serving layer — every model is light
> enough to run inline per request, which removes a whole class of
> stale-model bugs."

Show the Mermaid diagram from `SYSTEM_DESIGN.md` §2.

**[0:15–0:30] Forecasting**

> "Waste forecasting trains a RandomForestRegressor fresh, per zone, per
> request — on day-of-week, month, trend, and a 7-day lag feature. The
> confidence band comes from actual out-of-sample residual spread, not
> an assumption, and it falls back to a documented average when a zone
> has under 21 days of history."

Point at `app/ml/forecast.py`, specifically the `train_cutoff` /
residual_std computation.

**[0:30–0:45] Routing and maintenance**

> "Route optimization is a nearest-neighbor heuristic over haversine
> distances, compared against the original stop order — explicitly
> labelled as estimated, not real road routing. Maintenance risk is a
> transparent weighted score — mileage, overdue service, emergency-
> repair frequency, downtime trend — not a black-box probability, because
> the data doesn't support presenting it as one honestly."

Point at `app/optimization/routes.py::optimize_route` and
`app/ml/maintenance.py::score_vehicle`'s `WEIGHTS` dict.

**[0:45–1:05] The shared calculation layer**

> "The important architectural decision is here, in `calc.py`:
> `apply_simulation` takes a baseline and a set of adoption levers and
> returns a full recomputed cost/waste breakdown. The recommendation
> engine calls this exact function to estimate each intervention's
> impact, the dashboard calls it for the 'potential saving' preview, and
> the `/api/simulate` endpoint calls it for the interactive slider UI.
> Same function, same assumptions — a recommendation's claimed saving
> and the simulator's live output can never silently diverge."

Point at `app/calc.py::apply_simulation` and `app/recommendations.py`
calling it.

**[1:05–1:20] Data and limitations**

> "All underlying data is synthetic — deterministic, seeded, generated
> by `scripts/seed_data.py` with injected anomalies and a genuinely
> degrading subset of the vehicle fleet, so the models have real signal
> to find, not noise. Every projected number in the UI is labelled as a
> projection, not a measured outcome."

**[1:20–1:30] Close**

> "That's the system: one calculation layer, several lightweight models
> around it, and a frontend that never computes its own numbers — it
> only displays what the backend already computed consistently."

## Source of truth

This script and `SYSTEM_DESIGN.md` must stay consistent. If the code
changes, update `SYSTEM_DESIGN.md` first, then re-check this file
against it before recording.
