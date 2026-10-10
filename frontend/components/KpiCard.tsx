export function KpiCard({
  label,
  value,
  sublabel,
  tone = "default",
}: {
  label: string;
  value: string;
  sublabel?: string;
  tone?: "default" | "good" | "warn" | "bad";
}) {
  const toneColor = {
    default: "text-foreground",
    good: "text-accent",
    warn: "text-warn",
    bad: "text-danger",
  }[tone];

  return (
    <div className="card p-4 flex flex-col gap-1 min-w-0">
      <span className="text-xs uppercase tracking-wide text-muted">{label}</span>
      <span className={`text-2xl font-semibold font-mono ${toneColor} truncate`}>{value}</span>
      {sublabel && <span className="text-xs text-muted">{sublabel}</span>}
    </div>
  );
}
