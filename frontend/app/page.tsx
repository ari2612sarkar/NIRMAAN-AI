"use client";

import { useEffect, useState } from "react";
import {
  api,
  type Anomaly,
  type DashboardSummary,
  type ForecastResult,
  type MaintenanceRisk,
  type MapBin,
  type RouteOptimization,
  type ZoneSummary,
} from "@/lib/api";
import { KpiCard } from "@/components/KpiCard";
import { Section } from "@/components/Section";
import { WasteTrendChart } from "@/components/WasteTrendChart";
import { CostBreakdownChart } from "@/components/CostBreakdownChart";
import { RecommendationPanel } from "@/components/RecommendationPanel";
import { MaintenanceTable } from "@/components/MaintenanceTable";
import { RouteComparison } from "@/components/RouteComparison";
import { Simulator } from "@/components/Simulator";
import { MapViewClient } from "@/components/MapViewClient";
import { CopilotChat } from "@/components/CopilotChat";
import { AnomalyList } from "@/components/AnomalyList";

function fmtINR(n: number) {
  return `₹${Math.round(n).toLocaleString("en-IN")}`;
}

export default function Home() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [zones, setZones] = useState<ZoneSummary[]>([]);
  const [selectedZone, setSelectedZone] = useState<number | null>(null);
  const [trend, setTrend] = useState<{ date: string; quantity_kg: number }[]>([]);
  const [forecast, setForecast] = useState<ForecastResult | null>(null);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [maintenance, setMaintenance] = useState<MaintenanceRisk[]>([]);
  const [routeOpt, setRouteOpt] = useState<RouteOptimization | null>(null);
  const [mapBins, setMapBins] = useState<MapBin[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .dashboardSummary()
      .then(setSummary)
      .catch(() => setError("Could not reach the NIRMAAN AI backend. Is it running on port 8000?"));
    api.zones().then((z) => {
      setZones(z);
      if (z.length) setSelectedZone(z[0].zone_id);
    });
    api.anomalies().then(setAnomalies);
    api.maintenanceRisk().then(setMaintenance);
    api.mapBins().then(setMapBins);
  }, []);

  useEffect(() => {
    if (selectedZone == null) return;
    api.wasteTrend(selectedZone, 90).then(setTrend);
    api.zoneForecast(selectedZone, 7).then(setForecast);
    api.optimizeRoute(selectedZone).then(setRouteOpt);
  }, [selectedZone]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8">
        <div className="card p-6 max-w-md text-center">
          <p className="text-danger font-medium mb-2">Backend unreachable</p>
          <p className="text-sm text-muted">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 flex flex-col gap-6">
      <header className="flex flex-col sm:flex-row sm:items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            NIRMAAN <span className="text-accent">AI</span>
          </h1>
          <p className="text-sm text-muted mt-1">
            Waste Intelligence &amp; Cost Optimization — Predict → Prevent → Optimize → Maintain → Reduce
          </p>
        </div>
        <p className="text-xs text-muted border border-border rounded px-2 py-1 self-start sm:self-auto">
          100% synthetic demonstration data
        </p>
      </header>

      {!summary ? (
        <div className="text-muted text-sm">Loading dashboard…</div>
      ) : (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            <KpiCard label="Waste (30d)" value={`${(summary.total_waste_kg_30d / 1000).toFixed(1)} t`} />
            <KpiCard label="Operating cost (30d)" value={fmtINR(summary.operating_cost_30d)} />
            <KpiCard label="Overflow incidents" value={`${summary.overflow_incidents_30d}`} tone="warn" />
            <KpiCard label="High-risk bins" value={`${summary.high_risk_bin_count}`} tone="warn" />
            <KpiCard
              label="Potential monthly saving"
              value={fmtINR(summary.potential_monthly_saving)}
              tone="good"
              sublabel="at realistic combined adoption"
            />
          </div>

          <Section
            title="AI Priorities Today"
            subtitle={`${summary.priority_actions.length} actions could reduce projected operating cost by ${fmtINR(
              summary.priority_actions.reduce((s, a) => s + a.expected_monthly_saving, 0)
            )} this month`}
          >
            <RecommendationPanel recommendations={summary.top_recommendations} />
          </Section>

          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Section
                title="Waste Forecast"
                subtitle={forecast?.explanation}
                right={
                  <ZonePicker zones={zones} selected={selectedZone} onChange={setSelectedZone} />
                }
              >
                <WasteTrendChart history={trend} forecast={forecast} />
              </Section>
            </div>
            <Section title="Cost Breakdown (30d)">
              <CostBreakdownChart breakdown={summary.cost_breakdown} />
            </Section>
          </div>

          <div className="grid lg:grid-cols-2 gap-6">
            <Section title="Waste Anomalies" subtitle="Rolling 14-day z-score, |z| ≥ 2">
              <AnomalyList anomalies={anomalies} />
            </Section>
            <Section title="Collection Route Optimization" subtitle={routeOpt ? routeOpt.zone_name : undefined}>
              {routeOpt ? <RouteComparison data={routeOpt} /> : <p className="text-sm text-muted">Select a zone.</p>}
            </Section>
          </div>

          <Section title="Predictive Maintenance" subtitle="Vehicle fleet risk, ranked highest first">
            <MaintenanceTable vehicles={maintenance} />
          </Section>

          <div className="grid lg:grid-cols-2 gap-6">
            <Section title="Operations Map" subtitle="Bins across all zones — red = overflow risk">
              <div className="h-96 rounded-lg overflow-hidden">
                <MapViewClient bins={mapBins} />
              </div>
            </Section>
            <Section title="AI Copilot" subtitle="Rule-based, grounded in live computed data — no external LLM">
              <CopilotChat />
            </Section>
          </div>

          <Section title="Waste & Cost Reduction Simulator" subtitle="Adjust adoption levels and see the projected impact immediately">
            <Simulator />
          </Section>
        </>
      )}
    </div>
  );
}

function ZonePicker({
  zones,
  selected,
  onChange,
}: {
  zones: ZoneSummary[];
  selected: number | null;
  onChange: (id: number) => void;
}) {
  return (
    <select
      value={selected ?? ""}
      onChange={(e) => onChange(Number(e.target.value))}
      className="bg-surface-raised border border-border rounded-lg px-3 py-1.5 text-sm outline-none"
    >
      {zones.map((z) => (
        <option key={z.zone_id} value={z.zone_id}>
          {z.name}
        </option>
      ))}
    </select>
  );
}
