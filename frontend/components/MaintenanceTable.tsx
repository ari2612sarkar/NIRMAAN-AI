import type { MaintenanceRisk } from "@/lib/api";

const levelStyle: Record<string, string> = {
  high: "bg-danger/15 text-danger border-danger/30",
  medium: "bg-warn/15 text-warn border-warn/30",
  low: "bg-accent/15 text-accent border-accent/30",
};

export function MaintenanceTable({ vehicles }: { vehicles: MaintenanceRisk[] }) {
  return (
    <div className="overflow-x-auto scrollbar-thin">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-muted border-b border-border">
            <th className="py-2 pr-4 font-normal">Vehicle</th>
            <th className="py-2 pr-4 font-normal">Risk</th>
            <th className="py-2 pr-4 font-normal">Score</th>
            <th className="py-2 pr-4 font-normal">Odometer</th>
            <th className="py-2 pr-4 font-normal">Key drivers</th>
            <th className="py-2 pr-4 font-normal">Recommended action</th>
          </tr>
        </thead>
        <tbody>
          {vehicles.map((v) => (
            <tr key={v.vehicle_code} className="border-b border-border/50 last:border-0">
              <td className="py-2 pr-4 font-mono">{v.vehicle_code}</td>
              <td className="py-2 pr-4">
                <span className={`text-xs px-2 py-0.5 rounded border ${levelStyle[v.risk_level]}`}>
                  {v.risk_level}
                </span>
              </td>
              <td className="py-2 pr-4 font-mono">{v.risk_score}</td>
              <td className="py-2 pr-4 text-muted">{Math.round(v.odometer_km).toLocaleString()} km</td>
              <td className="py-2 pr-4 text-muted max-w-xs">{v.drivers.join(", ")}</td>
              <td className="py-2 pr-4">{v.recommended_action}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
