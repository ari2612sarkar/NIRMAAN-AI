import type { RouteOptimization } from "@/lib/api";

export function RouteComparison({ data }: { data: RouteOptimization }) {
  const pct = data.pct_distance_saved;
  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-lg border border-border p-4">
          <div className="text-xs uppercase text-muted mb-2">Baseline route</div>
          <div className="font-mono text-xl text-foreground">{data.baseline_distance_km} km</div>
          <div className="text-sm text-muted mt-1">₹{Math.round(data.baseline_cost.total).toLocaleString("en-IN")}</div>
        </div>
        <div className="rounded-lg border border-accent/30 bg-accent-soft p-4">
          <div className="text-xs uppercase text-muted mb-2">Optimized route</div>
          <div className="font-mono text-xl text-accent">{data.optimized_distance_km} km</div>
          <div className="text-sm text-muted mt-1">₹{Math.round(data.optimized_cost.total).toLocaleString("en-IN")}</div>
        </div>
      </div>
      <div className="h-2 w-full rounded-full bg-border overflow-hidden">
        <div className="h-full bg-accent" style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
      <p className="text-sm text-muted">
        {pct}% shorter ({data.distance_saved_km} km saved across {data.stop_count} stops), an estimated{" "}
        <span className="text-accent font-medium">₹{Math.round(data.cost_saved).toLocaleString("en-IN")}</span> saved
        on this route.
      </p>
      <p className="text-xs text-muted italic">{data.disclaimer}</p>
    </div>
  );
}
