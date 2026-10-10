# NIRMAAN AI — Submission Checklist

Updated 2026-10-10 after browser-based verification and actual video
recording became possible in this environment (Playwright + system
Chrome + Windows SAPI TTS + a bundled ffmpeg binary). Status reflects
what was actually checked/produced — nothing here is marked done based
on assumption.

| # | Deliverable | File / URL | Status | Verification performed | Remaining manual action |
|---|---|---|---|---|---|
| 1 | Project title & one-line description | `PORTAL_SUBMISSION.md`, `SUBMISSION.md` | **READY** | Content drafted and cross-checked for consistency between `SUBMISSION.md`, `SYSTEM_DESIGN.md`, and `PORTAL_SUBMISSION.md`. | Paste into portal form field. |
| 2 | Working demonstration video (≤3 min) | `submission/videos/nirmaan_ai_product_demo.mp4` | **READY** | **Actually recorded** — 153.96s, H.264+AAC, 1600×900, 6.5MB. Scripted Playwright session driving the real production app, real zone switch, real simulator slider drags with real recomputed output, synced SAPI voiceover. Full detail and frame-level QA in `submission/videos/VIDEO_VERIFICATION.md`. | Upload to the submission portal. |
| 3 | System-design walkthrough video | `submission/videos/nirmaan_ai_system_design.mp4` | **READY** | **Actually recorded** — 84.00s, H.264+AAC, 1600×900, 3.0MB. Shows the real Mermaid architecture diagram, the live Swagger `/docs` UI, byte-for-byte real source code (`routes.py`, `maintenance.py`, `calc.py`), and real captured test/build output. Full detail in `submission/videos/VIDEO_VERIFICATION.md`. | Upload to the submission portal. |
| 4 | Project write-up (300–500 words) | `SUBMISSION.md` | **READY** | 447 words (verified by word count); describes only implemented functionality; no invented partnerships/metrics. | None — ready to paste/attach. |
| 5 | Third-party tools/APIs/frameworks/models/libraries/datasets disclosure | `SUBMISSION.md`, `README.md`, `PORTAL_SUBMISSION.md` | **READY** | Cross-checked against `backend/requirements.txt` and `frontend/package.json`. No external LLM/API used (disclosed). No real datasets used — 100% synthetic (disclosed). Video-production tooling (Playwright, ffmpeg-static, Windows SAPI) is a local production aid, not part of the shipped application, and is not listed as an app dependency. | None. |
| 6 | Public repository or deployment URL (optional) | — | **NOT APPLICABLE / BLOCKED** | No git remote is configured (`git remote -v` returns empty) and the app is not deployed anywhere. | **Your decision**: push to a GitHub repo and/or deploy if the portal requests one, or leave blank if optional. |
| 7 | Eligibility & registration checks | — | **BLOCKED (not verifiable from this repo)** | No eligibility/registration data exists in this codebase to check. | **Confirm yourself** against the hackathon's actual rules. |
| 8 | Final submission portal confirmation | — | **BLOCKED** | Not submitted. | **Submit manually** via the official portal before the deadline. |
| 9 | README with accurate setup/run/test instructions | `README.md` | **READY** | Windows PowerShell + Git Bash setup blocks, test commands, known issues, demo-credentials disclosure (none — no auth). | None. |
| 10 | Architecture / system design documentation | `SYSTEM_DESIGN.md` | **READY** | Mermaid data-flow diagram verified against actual router/module names; Validation section with real test/curl output; honest Limitations section. | None. |
| 11 | Working application (backend + frontend) — **now browser-verified** | `http://127.0.0.1:8000`, `http://localhost:3000` | **READY** | Backend: `/api/health` → 200, 13/13 pytest passing. Frontend: `npm run build` compiles + type-checks clean. **Full browser-based functional smoke test performed with Playwright** (production build): dashboard KPIs load, 5 recommendation cards with Impact Scores render, zone switch redraws forecast chart, anomalies list populated, route comparison visible, 15/15 maintenance rows render, Leaflet map renders real markers, 5 simulator sliders present and a real drag changed output (₹0 → ₹4,390/month), AI Copilot returned a grounded answer — **zero browser console errors**. | None — already verified end to end. |
| 12 | Secrets/credentials hygiene | `.gitignore`, `backend/.env.example` | **READY** | No `.env`, `nirmaan.db`, `venv/`, or `node_modules/` tracked in git. `.env.example` has only a placeholder SQLite URL. | None. |
| 13 | Git repository state | — | **READY** | Clean at time of writing; commits preserved; no history rewrite or force-push; still no remote configured. | Commit this pass's changes (map-tile fix, videos, updated docs) — see note below. |

## Bugs found and fixed during this verification pass

1. **Dev-mode hydration stall under automation**: `next dev`'s Turbopack
   HMR WebSocket handshake failed in the automated browser session and
   silently stalled client-side hydration — the dashboard stayed on
   "Loading dashboard…" forever, with zero console errors to explain
   why. Root-caused by comparing against `npm run build && npm run
   start` (production), which loaded correctly with real data. **This
   is specific to dev mode under this automation setup** — recommend
   always demoing/judging against a production build
   (`npm run build && npm run start`), not `npm run dev`.
2. **Map tiles showed "API KEY REQUIRED"**: the CARTO dark-tile basemap
   used in `MapView.tsx` now requires an API key that was never
   configured. Fixed by switching to standard OpenStreetMap tiles with
   a CSS dark filter (`frontend/components/MapView.tsx`,
   `frontend/app/globals.css`), rebuilt, and reverified both by
   screenshot and in the recorded demo video.

Neither of these was visible from code review or `curl`-level checks in
the previous pass — both only surfaced once the app was actually driven
in a real browser.

## Summary of what remains for you to do, in order

1. Confirm hackathon eligibility/registration status (item 7) — not
   verifiable from this repo.
2. Watch both videos yourself once
   (`submission/videos/nirmaan_ai_product_demo.mp4`,
   `submission/videos/nirmaan_ai_system_design.mp4`) to confirm they
   meet your own bar — a synthesized voice narrates both, not a human.
3. Decide on and optionally set up a public GitHub repo / deployment URL
   (item 6) — not required unless the portal asks for one.
4. Fill in the official submission portal using `PORTAL_SUBMISSION.md`
   as copy-ready source text, attach/paste `SUBMISSION.md`, and upload
   both video files.
5. Submit before **October 10, 2026, 8:00 PM IST**.

Both videos are real, recorded, verified files sitting in
`submission/videos/` right now — not scripts, not screenshots, and not
yet uploaded anywhere.
