import type { Anomaly } from "@/lib/api";

export function AnomalyList({ anomalies }: { anomalies: Anomaly[] }) {
  if (anomalies.length === 0) {
    return <p className="text-sm text-muted">No anomalies detected in the current window.</p>;
  }
  return (
    <ul className="flex flex-col gap-2 max-h-72 overflow-y-auto scrollbar-thin pr-1">
      {anomalies.slice(0, 15).map((a, i) => (
        <li key={i} className="text-sm border border-border/60 rounded-lg px-3 py-2 flex items-start justify-between gap-3">
          <div>
            <span className={a.direction === "spike" ? "text-warn" : "text-accent"}>
              {a.direction === "spike" ? "▲" : "▼"}
            </span>{" "}
            <span className="text-foreground">{a.zone}</span>
            <span className="text-muted"> — {a.date}</span>
            <div className="text-xs text-muted mt-0.5">{a.explanation}</div>
          </div>
          <span className="font-mono text-xs text-muted shrink-0">z={a.z_score}</span>
        </li>
      ))}
    </ul>
  );
}
