const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`);
  return res.json();
}

export type Recommendation = {
  zone_id: number;
  zone_name: string;
  intervention_type: string;
  title: string;
  assumed_adoption_pct: number;
  expected_monthly_saving: number;
  implementation_cost: number;
  payback_days: number | null;
  confidence_pct: number;
  impact_score: number;
  drivers: string[];
  [key: string]: unknown;
};

export type DashboardSummary = {
  data_window: { start: string; end: string };
  total_waste_kg_30d: number;
  operating_cost_30d: number;
  cost_breakdown: {
    disposal: { landfill_cost: number; dry_processing_cost: number; recycling_revenue: number; net_cost: number; composting_cost: number };
    collection: number;
    overflow: number;
    maintenance: { scheduled_cost: number; emergency_cost: number; downtime_cost: number; total: number };
  };
  overflow_incidents_30d: number;
  high_risk_bin_count: number;
  landfill_diverted_pct: number;
  potential_monthly_saving: number;
  top_recommendations: Recommendation[];
  priority_actions: { title: string; impact_score: number; expected_monthly_saving: number }[];
};

export type ZoneSummary = {
  zone_id: number;
  name: string;
  zone_type: string;
  population_estimate: number;
  total_waste_kg_30d: number;
  segregation_pct: number;
  mixed_kg: number;
  wet_kg: number;
  dry_kg: number;
  recyclable_kg: number;
};

export type MaintenanceRisk = {
  vehicle_code: string;
  vehicle_type: string;
  odometer_km: number;
  risk_score: number;
  risk_level: "low" | "medium" | "high";
  factors: Record<string, number>;
  days_since_last_service: number;
  drivers: string[];
  recommended_action: string;
  estimated_cost_if_deferred: number;
};

export type HighRiskBin = {
  bin_code: string;
  location_name: string;
  latitude: number;
  longitude: number;
  waste_category: string;
  avg_fill_pct_last5: number;
  missed_rate_last5: number;
  risk_score: number;
  explanation: string;
};

export type MapBin = {
  bin_code: string;
  latitude: number;
  longitude: number;
  waste_category: string;
  zone_name: string;
  location_name: string;
  status: string;
  overflow_risk: boolean;
};

export type ForecastResult = {
  method: string;
  predictions: { date: string; predicted_kg: number; lower_kg: number; upper_kg: number }[];
  feature_importance: Record<string, number>;
  explanation: string;
  zone_id: number;
  zone_name: string;
};

export type Anomaly = {
  zone: string;
  date: string;
  quantity_kg: number;
  rolling_avg_kg: number;
  z_score: number;
  direction: "spike" | "drop";
  explanation: string;
};

export type RouteOptimization = {
  zone_id: number;
  zone_name: string;
  stop_count: number;
  baseline_distance_km: number;
  optimized_distance_km: number;
  distance_saved_km: number;
  pct_distance_saved: number;
  baseline_cost: { total: number; fuel_cost: number; labour_cost: number; vehicle_wear_cost: number };
  optimized_cost: { total: number; fuel_cost: number; labour_cost: number; vehicle_wear_cost: number };
  cost_saved: number;
  disclaimer: string;
};

export type SimulationInputs = {
  zone_id?: number | null;
  segregation_adoption_pct: number;
  composting_adoption_pct: number;
  collection_frequency_change_pct: number;
  route_optimization_efficiency_pct: number;
  predictive_maintenance_adoption_pct: number;
};

export type SimulationResult = {
  window: { start: string; end: string };
  baseline: Record<string, number | Record<string, unknown>>;
  simulated: Record<string, number | Record<string, unknown>>;
  monthly_saving: number;
  annual_saving_projection: number;
  note: string;
};

export const api = {
  dashboardSummary: () => get<DashboardSummary>("/api/dashboard/summary"),
  zones: () => get<ZoneSummary[]>("/api/dashboard/zones"),
  wasteTrend: (zoneId?: number, days = 90) =>
    get<{ date: string; quantity_kg: number }[]>(
      `/api/dashboard/waste-trend?days=${days}${zoneId ? `&zone_id=${zoneId}` : ""}`
    ),
  zoneForecast: (zoneId: number, horizonDays = 7) =>
    get<ForecastResult>(`/api/forecast/zone/${zoneId}?horizon_days=${horizonDays}`),
  anomalies: () => get<Anomaly[]>("/api/forecast/anomalies"),
  maintenanceRisk: () => get<MaintenanceRisk[]>("/api/maintenance/risk"),
  highRiskBins: () => get<HighRiskBin[]>("/api/maintenance/high-risk-bins"),
  optimizeRoute: (zoneId: number) => get<RouteOptimization>(`/api/routes/optimize/${zoneId}`),
  recommendations: (limit = 10) => get<Recommendation[]>(`/api/recommendations?limit=${limit}`),
  mapBins: () => get<MapBin[]>("/api/map/bins"),
  simulate: (inputs: SimulationInputs) => post<SimulationResult>("/api/simulate", inputs),
  askCopilot: (question: string) => post<{ question: string; answer: string; tool_used: string }>("/api/copilot/ask", { question }),
};
