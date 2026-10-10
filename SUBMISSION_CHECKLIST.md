# NIRMAAN AI — Submission Checklist

Generated during final release verification on 2026-10-10. Status
reflects what was actually checked in this repository/environment —
nothing here is marked done based on assumption.

| # | Deliverable | File / URL | Status | Verification performed | Remaining manual action |
|---|---|---|---|---|---|
| 1 | Project title & one-line description | `PORTAL_SUBMISSION.md`, `SUBMISSION.md` | **READY** | Content drafted and cross-checked for consistency between `SUBMISSION.md`, `SYSTEM_DESIGN.md`, and `PORTAL_SUBMISSION.md`. | Paste into portal form field. |
| 2 | Working demonstration video (≤3 min) | — | **BLOCKED** | Not recorded. `DEMO_SCRIPT.md` is ready and the app is verified running (backend 13/13 tests pass, frontend builds clean, both servers respond 200). | **Record the screen demo yourself** following `DEMO_SCRIPT.md`, then upload per portal instructions. |
| 3 | System-design walkthrough video | — | **BLOCKED** | Not recorded. `SYSTEM_DESIGN_WALKTHROUGH.md` script + checklist ready. | **Record the walkthrough yourself**, then upload. |
| 4 | Project write-up (300–500 words) | `SUBMISSION.md` | **READY** | Rewritten to 447 words (verified by word count); describes only implemented functionality; no invented partnerships/metrics. | None — ready to paste/attach. |
| 5 | Third-party tools/APIs/frameworks/models/libraries/datasets disclosure | `SUBMISSION.md`, `README.md`, `PORTAL_SUBMISSION.md` | **READY** | Cross-checked against `backend/requirements.txt` and `frontend/package.json` — FastAPI, SQLAlchemy, scikit-learn, pandas/numpy, Faker, pytest, Next.js, React, Tailwind, Recharts, Leaflet/react-leaflet. No external LLM/API used (explicitly disclosed). No real datasets used — 100% synthetic, disclosed. | None. |
| 6 | Public repository or deployment URL (optional) | — | **NOT APPLICABLE / BLOCKED** | No git remote is configured (`git remote -v` returns empty) and the app is not deployed anywhere. | **Your decision**: push to a GitHub repo and/or deploy (see README "Future deployment plan") if the portal requests one, or leave blank if optional. |
| 7 | Eligibility & registration checks | — | **BLOCKED (not verifiable from this repo)** | No eligibility/registration data exists in this codebase to check. | **Confirm yourself** against the hackathon's actual rules (team size, registration status, submission window) — this cannot be verified from the repository. |
| 8 | Final submission portal confirmation | — | **BLOCKED** | Not submitted. | **Submit manually** via the official portal before the deadline; this session has no access to any submission portal. |
| 9 | README with accurate setup/run/test instructions | `README.md` | **READY** | Updated with Windows PowerShell + Git Bash setup blocks, test commands, known issues, demo-credentials disclosure (none — no auth), screenshots disclosure (none captured — no browser tooling available). | None. |
| 10 | Architecture / system design documentation | `SYSTEM_DESIGN.md` | **READY** | Added Mermaid data-flow diagram verified against actual router/module names in `backend/app/`; added a Validation section with real test/curl output from this pass; added an honest Limitations section. | None. |
| 11 | Working application (backend + frontend) | `http://127.0.0.1:8000`, `http://localhost:3000` | **READY** | Backend: `/api/health` → 200, 13/13 pytest passing, all 10 zones return 200 across forecast/route/recommendation endpoints, 4 numerical-consistency spot checks passed (overflow-risk direction, mass conservation, route-optimization monotonicity, single cost-calculation source). Frontend: `npm run build` compiles + type-checks clean, page returns 200 and contains expected title text. **UI was not visually verified in a browser** — no Chrome extension connected in this environment. | **Open `http://localhost:3000` yourself and click through it** before recording the demo video — see the manual smoke-test checklist below. |
| 12 | Secrets/credentials hygiene | `.gitignore`, `backend/.env.example` | **READY** | Verified: no `.env`, no `nirmaan.db`, no `venv/`, no `node_modules/` tracked in git (`git ls-files` checked). `.env.example` contains only a placeholder SQLite URL, no real credentials. | None. |
| 13 | Git repository state | — | **READY** | `git status` clean at start and end of this pass; 3 pre-existing commits preserved; no history rewrite, no force-push attempted, no remote configured so no push was possible or attempted. | Decide whether to add a remote and push (see item 6). |

## Manual smoke-test checklist (since browser automation was unavailable here)

Run this yourself in an actual browser before recording the demo:

1. Open `http://localhost:3000` — dashboard loads, 5 KPI cards show
   numbers (not stuck on "Loading dashboard…").
2. "AI Priorities Today" shows at least one recommendation card with an
   Impact Score and ₹ figures.
3. Change the zone dropdown in "Waste Forecast" — chart redraws with a
   dashed forecast line and shaded band.
4. "Waste Anomalies" list shows entries with explanations.
5. "Collection Route Optimization" shows baseline vs. optimized distance
   and cost for the selected zone.
6. "Predictive Maintenance" table is populated, sorted by risk score.
7. "Operations Map" renders a dark map with colored bin markers.
8. Drag a slider in the simulator — the right-hand numbers update within
   ~1 second.
9. Click a suggested question in the AI Copilot — a grounded text answer
   appears.
10. Open browser dev tools (F12) → Console tab — confirm no red errors.

## Summary of what remains for you to do, in order

1. Confirm hackathon eligibility/registration status (item 7) — not
   verifiable from this repo.
2. Run the manual smoke-test checklist above in a real browser.
3. Record the 3-minute demo video using `DEMO_SCRIPT.md`.
4. Record the system-design walkthrough using
   `SYSTEM_DESIGN_WALKTHROUGH.md`.
5. Decide on and optionally set up a public GitHub repo / deployment URL
   (item 6) — not required unless the portal asks for one.
6. Fill in the official submission portal using `PORTAL_SUBMISSION.md`
   as copy-ready source text, attach/paste `SUBMISSION.md`, upload both
   videos.
7. Submit before **October 10, 2026, 8:00 PM IST**.

No step above has been performed on your behalf beyond what this
checklist states as READY — videos were not recorded, nothing was
submitted, and no deployment or repository push was made.
