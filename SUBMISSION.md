# NIRMAAN AI — Waste Intelligence & Cost Optimization Platform

**Predict less waste. Collect smarter. Maintain proactively. Spend less.**

## The problem

Municipal waste operations in India are largely reactive: collection
runs on a fixed schedule regardless of actual demand, vehicle
maintenance happens after a breakdown rather than before one, and
there's no systematic link between "waste generation is rising here"
and "here is a specific, costed action to reduce it." The result is
higher fuel and labour spend, missed pickups and overflow, avoidable
emergency repairs, and almost no visibility into which interventions
(segregation, composting, commercial-specific collection) would
actually move the numbers.

## The approach

NIRMAAN AI connects the full waste lifecycle in one system rather than
treating forecasting, routing, maintenance, and cost as separate
dashboards. A trained regression model forecasts daily waste generation
per zone with a confidence interval; a rolling z-score detector flags
abnormal spikes or drops with the exact comparison shown. A
nearest-neighbor routing heuristic compares a baseline collection route
against an optimized one on real distance and ₹ cost (distances are
estimated straight-line/haversine, not road routing — disclosed in the
UI). A transparent, weighted risk score — not a black-box probability —
prioritizes vehicles for maintenance using mileage, service-overdue
status, recent emergency-repair frequency, and downtime trend. A
rules-based recommendation engine proposes costed interventions
(segregation, composting, commercial programs) per zone, each with a
documented Impact Score, expected saving, implementation cost, and
payback period.

The signature feature is the interactive simulator: five adjustable
levers recompute projected waste, distance, overflow, and total
operating cost immediately. Every projected number — in the
recommendation engine, the dashboard's "potential saving" preview, and
the simulator itself — is produced by the same shared calculation
function over the same documented cost assumptions, so they can never
silently disagree. A rule-based AI Copilot answers questions by calling
those same backend functions directly; it has no external LLM
dependency and cannot invent a number it didn't actually compute.

## Users and pilot plan

Intended users are municipal operations managers, maintenance
coordinators, and sustainability teams at the ward/zone, campus, or
township level. A credible pilot would run the platform against one
real zone's actual bin/vehicle data for several weeks without acting on
it, to validate forecast and risk-score accuracy before implementing
the single highest-impact recommendation and comparing measured
outcomes to the simulator's prior projection.

## Honesty about results

**All data in this build is synthetic** (deterministic, seeded,
disclosed in-app and in the README) — there is no real municipal
deployment, pilot, or measured outcome to report. Maintenance risk is
an explainable heuristic, not a statistically calibrated failure model.
Every dashboard/simulator figure is a projection from documented
formulas, never a claim of real-world measured savings.
