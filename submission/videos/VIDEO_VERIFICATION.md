# Video Verification

Both files below were produced in this environment, from the actual
running application, and verified with `ffprobe`/frame extraction
before being written here — nothing in this document is asserted
without having been checked.

## 1. `nirmaan_ai_product_demo.mp4`

| Property | Value |
|---|---|
| Path | `submission/videos/nirmaan_ai_product_demo.mp4` |
| Duration | **153.96s** (target: 150–175s, cap 180s — within range) |
| Format | MP4 (isom), H.264 video + AAC audio |
| Video | 1600×900, 25fps, yuv420p |
| Audio | AAC, mono, 44.1kHz, ~160kbps |
| File size | 6,518,784 bytes (6.5 MB) |
| Audio/video sync | Video 153.960s vs. audio 153.948s — within 12ms |

**How it was produced**: scripted with Playwright driving the system's
installed Chrome (`channel: "chrome"`) against the actual production
build of the frontend (`npm run build && npm run start`) and the real
backend, recording the browser via Playwright's built-in `recordVideo`
(captures genuine rendered frames, not synthesized/mocked). Actions
performed live against the real app: scrolled the dashboard, switched
the zone dropdown (triggering a real forecast re-fetch and chart
redraw), scrolled through live recommendation cards, the maintenance
table, and the route-optimization comparison, then dragged two actual
simulator sliders with the mouse and let the real `/api/simulate` call
recompute the displayed numbers. Narration was synthesized separately
with Windows SAPI (`Microsoft David Desktop` voice) per script segment,
padded with silence to the intended on-screen dwell time for that
segment, concatenated into one 150.00s track, and muxed onto the
153.96s video recording with `ffmpeg` (`-c:v libx264 -c:a aac
-shortest`). The ~4s difference between the audio track and the final
video length is trailing silent video at the end (held on the closing
KPI frame) — not a sync error.

**Visual QA performed**: 8 frames extracted via `ffmpeg -ss <t>
-frames:v 1` at 5/25/45/65/85/105/130/150s and inspected. Confirmed:
real KPI numbers, real recommendation cards with Impact Scores, a real
zone switch with the forecast chart and confidence band redrawing, the
real operations map (OpenStreetMap, dark-filtered) with colored bin
markers, and the simulator showing a real recalculated result
(₹3,55,758/month projected saving after moving two sliders) with the
"Simulated/projected figures from documented formulas — not measured
real-world results" disclaimer visible on screen.

**A bug was found and fixed during this process**: the map tiles
initially showed "API KEY REQUIRED" placeholders (the CARTO free
dark-tile endpoint used in `MapView.tsx` now requires an API key).
Fixed by switching to standard OpenStreetMap tiles with a CSS dark
filter (`frontend/components/MapView.tsx`, `frontend/app/globals.css`),
rebuilt, and reverified before recording.

## 2. `nirmaan_ai_system_design.mp4`

| Property | Value |
|---|---|
| Path | `submission/videos/nirmaan_ai_system_design.mp4` |
| Duration | **84.00s** (target: 60–90s — within range) |
| Format | MP4 (isom), H.264 video + AAC audio |
| Video | 1600×900, yuv420p |
| Audio | AAC, mono, 44.1kHz, ~160kbps |
| File size | 3,030,964 bytes (3.0 MB) |
| Audio/video sync | Both streams exactly 84.000s (video explicitly trimmed to match the audio track with `-t 84`) |

**How it was produced**: narration synthesized the same way as video 1
(5 segments, Windows SAPI, padded to assigned on-screen durations
summing to 84.00s exactly). The visual track was recorded with
Playwright navigating, in order: (1) a local HTML page rendering the
actual Mermaid diagram from `SYSTEM_DESIGN.md` via mermaid.js,
cross-checked against real module names; (2) the **live** FastAPI
Swagger UI at `http://127.0.0.1:8000/docs`, showing the real registered
endpoint groups (`forecast`, `maintenance`, `routes`, `recommendations`,
`simulate`, `map`); (3) two local HTML pages displaying the **exact,
unmodified text** of `backend/app/optimization/routes.py`'s
`optimize_route` function and `backend/app/ml/maintenance.py`'s
`WEIGHTS` dict, read programmatically from the actual files (not
retyped, to guarantee fidelity); (4) the same treatment for
`backend/app/calc.py`'s `apply_simulation` function; (5) a local HTML
page reproducing the real, previously-captured terminal output of
`python -m pytest tests/ -q` (`13 passed in 3.12s`) and `npm run build`
(compiled/type-checked/generated successfully). The raw recording ran
94.72s (network/file-navigation latency pushed some segments past their
budgeted dwell time); it was trimmed to the first 84.00s with `ffmpeg
-t 84` to land within the 60–90s requirement, and confirmed via frame
extraction that the trim point lands cleanly on the terminal/validation
screen, not mid-transition.

**Visual QA performed**: 5 frames extracted at 3/20/40/60/80s and
inspected. Confirmed: the Mermaid diagram renders correctly and matches
the repository's actual module layout; the Swagger UI shows real
endpoint paths matching `backend/app/api/*.py`; the source-code frames
show byte-for-byte real file content (e.g. `WEIGHTS = {"mileage": 0.25,
"service_overdue": 0.30, "emergency_frequency": 0.30, "downtime_trend":
0.15}` exactly matching `app/ml/maintenance.py`); the closing frame
shows the real test/build output.

## What was NOT done

- No lip-sync or avatar — this is screen recording + voiceover, not a
  talking-head video.
- TTS voice quality is a synthesized Windows SAPI voice (David), not a
  human narrator — clearly a machine voice, not a claim of human
  narration.
- Neither video has been uploaded anywhere. Both exist only as local
  files in `submission/videos/` at the time of this writing.
