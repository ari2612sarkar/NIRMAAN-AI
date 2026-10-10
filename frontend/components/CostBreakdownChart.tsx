"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { DashboardSummary } from "@/lib/api";

const COLORS = ["#5b8def", "#35d0ac", "#e8b84b", "#e2655b"];

export function CostBreakdownChart({ breakdown }: { breakdown: DashboardSummary["cost_breakdown"] }) {
  const data = [
    { name: "Collection", value: Math.round(breakdown.collection) },
    { name: "Disposal", value: Math.round(breakdown.disposal.net_cost) },
    { name: "Maintenance", value: Math.round(breakdown.maintenance.total) },
    { name: "Overflow", value: Math.round(breakdown.overflow) },
  ];

  return (
    <div className="h-56 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ left: 16, right: 16 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#253040" horizontal={false} />
          <XAxis type="number" tick={{ fill: "#8a99ab", fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fill: "#e7edf5", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            width={90}
          />
          <Tooltip
            formatter={(v) => `₹${Number(v).toLocaleString("en-IN")}`}
            contentStyle={{ background: "#171f28", border: "1px solid #253040", borderRadius: 8, fontSize: 12 }}
          />
          <Bar dataKey="value" radius={[0, 6, 6, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
