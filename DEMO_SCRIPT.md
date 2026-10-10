# NIRMAAN AI — 3-Minute Demo Script

Target runtime: ≤3:00. Record at `http://localhost:3000` with both the
backend (`:8000`) and frontend (`:3000`) already running and the page
freshly loaded (so all sections have real data, not loading spinners).

Each beat lists: the exact page/control, the action to perform, what
should visibly happen, suggested narration, and a fallback if the
interaction doesn't behave as expected live.

---

### 0:00–0:15 — Introduction

- **Page/control**: top of the dashboard (header + KPI row).
- **Action**: just let it sit on screen; no clicking yet.
- **Expected result**: "NIRMAAN AI" header, tagline, "100% synthetic
  demonstration data" badge, and the 5 KPI cards (Waste, Operating cost,
  Overflow incidents, High-risk bins, Potential monthly saving).
- **Narration**: "NIRMAAN AI is an AI operations platform for municipal
  waste management — it connects forecasting, collection routing,
  maintenance, and cost into one closed loop instead of separate
  dashboards."
- **Fallback**: if KPIs still show "Loading dashboard…", wait 2–3
  seconds — the first load fetches five endpoints in parallel.

### 0:15–0:45 — AI Priorities Today

- **Page/control**: "AI Priorities Today" section, just below the KPIs.
- **Action**: scroll to it; point at the top recommendation card.
- **Expected result**: a ranked list of interventions, each with an
  Impact Score, estimated monthly saving, implementation cost, payback
  period, confidence %, and the specific drivers behind it.
- **Narration**: "Every morning this ranks the highest-impact action
  available — not a generic alert, but a costed recommendation with the
  exact reasons it was generated, like overflow incidents in a specific
  zone."
- **Fallback**: if the list is empty, that's a real (if unlikely)
  "nothing urgent right now" state — say so rather than treating it as
  broken.

### 0:45–1:15 — Forecasting and anomalies

- **Page/control**: "Waste Forecast" section (zone dropdown, top right
  of that card) and "Waste Anomalies" section below it.
- **Action**: open the zone dropdown, pick a different zone.
- **Expected result**: the chart redraws — solid historical line,
  dashed forecast line with a shaded confidence band; the explanation
  text above updates (e.g. "driven mainly by day-of-week pattern").
  Scroll to Waste Anomalies and point at one flagged entry.
- **Narration**: "This is a trained model, not a guess — it shows its
  confidence band and explains what's driving the forecast. Below it,
  anomaly detection flags days that broke the recent pattern, with the
  exact comparison shown."
- **Fallback**: if a zone shows the "insufficient history" fallback
  message instead of a forest-based forecast, pick a different zone —
  that fallback is itself a deliberate, honest feature, not a bug.

### 1:15–1:45 — Maintenance and route optimization

- **Page/control**: "Predictive Maintenance" table, and "Collection
  Route Optimization" card (same zone as the forecast selector).
- **Action**: point at the top row of the maintenance table (highest
  risk score); then point at the baseline-vs-optimized route numbers.
- **Expected result**: a risk level badge (high/medium/low), numeric
  score, listed drivers (e.g. "repeated recent emergency repairs"), and
  a recommended action; the route card shows baseline km/₹ vs. optimized
  km/₹ and a % distance saved.
- **Narration**: "Maintenance risk is transparent — you can see exactly
  why a vehicle is flagged. And for the same zone, here's today's
  collection route versus an optimized one, with the real distance and
  rupee difference — not a mockup."
- **Fallback**: if a zone has only 1–2 bins (thin route), switch to a
  zone with more locations for a clearer before/after contrast.

### 1:45–2:25 — The simulator (signature moment)

- **Page/control**: "Waste & Cost Reduction Simulator" section, bottom
  of the page.
- **Action**: drag the "Source segregation adoption" slider from 0 to
  ~50; then also drag "Route optimization efficiency" up.
- **Expected result**: the right-hand comparison column updates live —
  mixed waste falls, landfill-diverted % rises, total operating cost
  drops, and the "Projected saving" box recalculates ₹/month and ₹/year.
- **Narration**: "This is the signature feature — adjust any
  combination of these levers and see the operational and financial
  impact immediately, calculated with the same formulas as the
  recommendations you just saw — never a separate, disconnected number."
- **Fallback**: if the comparison panel looks frozen, wait ~300ms — it
  debounces slider input before recalculating.

### 2:25–2:45 — AI Copilot

- **Page/control**: "AI Copilot" card (next to the Operations Map).
- **Action**: click one suggested-question chip, e.g. "What if
  segregation increased to 60%?".
- **Expected result**: a grounded answer appears with real numbers
  (e.g. specific kg and ₹ figures) and names the backend tool it used.
- **Narration**: "No external AI model here — it's answering by calling
  the exact same backend functions as the rest of the app, so it can't
  invent a number it didn't actually compute."
- **Fallback**: if a typed question doesn't match a known topic, click
  one of the suggestion chips instead — they're guaranteed to resolve.

### 2:45–3:00 — Close

- **Page/control**: scroll back to the top KPI row.
- **Action**: no interaction — hold the frame.
- **Narration**: "Predict less waste. Collect smarter. Maintain
  proactively. Spend less. Every number you just saw is a documented
  projection from a transparent formula — not a claim of real-world
  measured results. That's NIRMAAN AI."

---

**Do not** improvise additional claims during recording (e.g. "this is
live in City X") — every number on screen is from the synthetic demo
dataset, and the script above is written to say so explicitly in the
close.
