import type { Recommendation } from "@/lib/api";

function fmtINR(n: number) {
  return `₹${Math.round(n).toLocaleString("en-IN")}`;
}

export function RecommendationPanel({ recommendations }: { recommendations: Recommendation[] }) {
  if (recommendations.length === 0) {
    return <p className="text-sm text-muted">No interventions recommended right now — metrics look healthy.</p>;
  }

  return (
    <div className="flex flex-col gap-3">
      {recommendations.map((r, i) => (
        <div key={i} className="rounded-lg border border-border bg-surface-raised p-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <span className="text-xs uppercase tracking-wide text-accent">{r.intervention_type.replace(/_/g, " ")}</span>
              <h3 className="font-medium text-foreground mt-0.5">{r.title}</h3>
            </div>
            <div className="text-right shrink-0">
              <div className="font-mono text-lg text-accent">{r.impact_score}</div>
              <div className="text-[10px] text-muted uppercase">impact score</div>
            </div>
          </div>
          <div className="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-2 text-sm">
            <Stat label="Est. monthly saving" value={fmtINR(r.expected_monthly_saving)} />
            <Stat label="Implementation cost" value={fmtINR(r.implementation_cost)} />
            <Stat label="Payback" value={r.payback_days ? `${r.payback_days} days` : "—"} />
            <Stat label="Confidence" value={`${r.confidence_pct}%`} />
          </div>
          <ul className="mt-3 flex flex-wrap gap-2">
            {r.drivers.map((d, j) => (
              <li key={j} className="text-xs text-muted bg-background/40 border border-border rounded px-2 py-1">
                {d}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="font-mono text-foreground">{value}</div>
      <div className="text-[10px] text-muted uppercase tracking-wide">{label}</div>
    </div>
  );
}
