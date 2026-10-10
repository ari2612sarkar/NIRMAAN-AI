"use client";

import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ForecastResult } from "@/lib/api";

type Point = {
  date: string;
  historical?: number;
  forecast?: number;
  lower?: number;
  upperBand?: number; // upper - lower, stacked on top of lower for a shaded band
};

export function WasteTrendChart({
  history,
  forecast,
}: {
  history: { date: string; quantity_kg: number }[];
  forecast?: ForecastResult | null;
}) {
  const points: Point[] = history.map((h) => ({ date: h.date, historical: h.quantity_kg }));

  if (forecast) {
    for (const p of forecast.predictions) {
      points.push({
        date: p.date,
        forecast: p.predicted_kg,
        lower: p.lower_kg,
        upperBand: Math.max(p.upper_kg - p.lower_kg, 0),
      });
    }
  }

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={points} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#253040" />
          <XAxis
            dataKey="date"
            tick={{ fill: "#8a99ab", fontSize: 11 }}
            minTickGap={40}
            axisLine={{ stroke: "#253040" }}
            tickLine={false}
          />
          <YAxis tick={{ fill: "#8a99ab", fontSize: 11 }} axisLine={false} tickLine={false} width={50} />
          <Tooltip
            contentStyle={{ background: "#171f28", border: "1px solid #253040", borderRadius: 8, fontSize: 12 }}
            labelStyle={{ color: "#e7edf5" }}
          />
          <Area
            type="monotone"
            dataKey="lower"
            stackId="band"
            stroke="none"
            fill="transparent"
            isAnimationActive={false}
          />
          <Area
            type="monotone"
            dataKey="upperBand"
            stackId="band"
            stroke="none"
            fill="#35d0ac"
            fillOpacity={0.12}
            isAnimationActive={false}
            name="Confidence band"
          />
          <Line type="monotone" dataKey="historical" stroke="#5b8def" strokeWidth={2} dot={false} name="Historical" />
          <Line
            type="monotone"
            dataKey="forecast"
            stroke="#35d0ac"
            strokeWidth={2}
            strokeDasharray="5 4"
            dot={false}
            name="Forecast"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
