"use client";

import { useEffect, useState } from "react";
import { api, type SimulationResult } from "@/lib/api";

type Levers = {
  segregation_adoption_pct: number;
  composting_adoption_pct: number;
  collection_frequency_change_pct: number;
  route_optimization_efficiency_pct: number;
  predictive_maintenance_adoption_pct: number;
};

const DEFAULT_LEVERS: Levers = {
  segregation_adoption_pct: 0,
  composting_adoption_pct: 0,
  collection_frequency_change_pct: 0,
  route_optimization_efficiency_pct: 0,
  predictive_maintenance_adoption_pct: 0,
};

const SLIDERS: { key: keyof Levers; label: string; min: number; max: number }[] = [
  { key: "segregation_adoption_pct", label: "Source segregation adoption", min: 0, max: 100 },
  { key: "composting_adoption_pct", label: "Composting adoption", min: 0, max: 100 },
  { key: "route_optimization_efficiency_pct", label: "Route optimization efficiency", min: 0, max: 100 },
  { key: "predictive_maintenance_adoption_pct", label: "Predictive maintenance adoption", min: 0, max: 100 },
  { key: "collection_frequency_change_pct", label: "Collection frequency change", min: -50, max: 50 },
];

function fmtINR(n: number) {
  return `₹${Math.round(n).toLocaleString("en-IN")}`;
}

export function Simulator() {
  const [levers, setLevers] = useState<Levers>(DEFAULT_LEVERS);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let active = true;
    setLoading(true);
    const timeout = setTimeout(() => {
      api
        .simulate({ zone_id: null, ...levers })
        .then((r) => {
          if (active) setResult(r);
        })
        .catch(() => {})
        .finally(() => active && setLoading(false));
    }, 250);
    return () => {
      active = false;
      clearTimeout(timeout);
    };
  }, [levers]);

  const baseline = result?.baseline;
  const simulated = result?.simulated;

  return (
    <div className="grid lg:grid-cols-2 gap-6">
      <div className="flex flex-col gap-5">
        {SLIDERS.map((s) => (
          <div key={s.key}>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-muted">{s.label}</span>
              <span className="font-mono text-foreground">{levers[s.key]}%</span>
            </div>
            <input
              type="range"
              min={s.min}
              max={s.max}
              value={levers[s.key]}
              onChange={(e) => setLevers((prev) => ({ ...prev, [s.key]: Number(e.target.value) }))}
              className="w-full accent-[#35d0ac]"
            />
          </div>
        ))}
        <button
          onClick={() => setLevers(DEFAULT_LEVERS)}
          className="self-start text-xs text-muted hover:text-foreground border border-border rounded px-3 py-1.5 mt-1"
        >
          Reset to baseline
        </button>
      </div>

      <div className={`flex flex-col gap-3 transition-opacity ${loading ? "opacity-60" : "opacity-100"}`}>
        {baseline && simulated && (
          <>
            <ComparisonRow
              label="Total waste"
              baseline={`${Math.round(baseline.total_waste_kg as number).toLocaleString()} kg`}
              simulated={`${Math.round(simulated.total_waste_kg as number).toLocaleString()} kg`}
            />
            <ComparisonRow
              label="Landfill diverted"
              baseline={`${baseline.landfill_diverted_pct}%`}
              simulated={`${simulated.landfill_diverted_pct}%`}
              good
            />
            <ComparisonRow
              label="Distance travelled"
              baseline={`${Math.round(baseline.total_distance_km as number).toLocaleString()} km`}
              simulated={`${Math.round(simulated.total_distance_km as number).toLocaleString()} km`}
            />
            <ComparisonRow
              label="Overflow incidents"
              baseline={`${baseline.overflow_incidents}`}
              simulated={`${simulated.overflow_incidents}`}
            />
            <ComparisonRow
              label="Total operating cost"
              baseline={fmtINR(baseline.total_operating_cost as number)}
              simulated={fmtINR(simulated.total_operating_cost as number)}
              good
            />
            <div className="mt-2 rounded-lg border border-accent/30 bg-accent-soft p-4">
              <div className="text-xs uppercase text-muted">Projected saving</div>
              <div className="font-mono text-2xl text-accent mt-1">{fmtINR(result!.monthly_saving)}/month</div>
              <div className="text-sm text-muted mt-1">≈ {fmtINR(result!.annual_saving_projection)}/year projected</div>
            </div>
            <p className="text-xs text-muted italic">{result!.note}</p>
          </>
        )}
      </div>
    </div>
  );
}

function ComparisonRow({
  label,
  baseline,
  simulated,
  good,
}: {
  label: string;
  baseline: string;
  simulated: string;
  good?: boolean;
}) {
  return (
    <div className="flex items-center justify-between text-sm border-b border-border/50 pb-2">
      <span className="text-muted">{label}</span>
      <span className="flex items-center gap-2 font-mono">
        <span className="text-muted line-through">{baseline}</span>
        <span>→</span>
        <span className={good ? "text-accent" : "text-foreground"}>{simulated}</span>
      </span>
    </div>
  );
}
