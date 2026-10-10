from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import copilot, dashboard, forecast, maintenance, map_data, recommendations_api, routes_opt, simulate

app = FastAPI(
    title="NIRMAAN AI",
    description="Waste Intelligence & Cost Optimization Platform — Predict, Prevent, Optimize, Maintain, Reduce.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(forecast.router)
app.include_router(maintenance.router)
app.include_router(routes_opt.router)
app.include_router(recommendations_api.router)
app.include_router(simulate.router)
app.include_router(map_data.router)
app.include_router(copilot.router)


@app.get("/")
def root():
    return {"name": "NIRMAAN AI", "status": "ok", "docs": "/docs"}


@app.get("/api/health")
def health():
    return {"status": "ok"}
