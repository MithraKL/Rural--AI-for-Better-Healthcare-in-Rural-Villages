import type {
  District, VillageSummary, VillageDetail, RiskPrediction, Explanation, Priority,
  InterventionOption, SimulationRequest, SimulationResult, ResourcePoolIn,
  ResourceOptimizationResult, FacilityMismatch, EarlyWarning, DatasetMetadata,
  UploadResponse, DashboardKPIs, Facility,
} from "@/types";

const BASE = "/api";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: init?.body && !(init.body instanceof FormData) ? { "Content-Type": "application/json" } : undefined,
    ...init,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  dashboardKpis: () => req<DashboardKPIs>("/dashboard/kpis"),

  districts: () => req<District[]>("/districts/"),

  villages: (params?: { district_id?: number; risk_category?: string; paradox_only?: boolean; search?: string }) => {
    const qs = new URLSearchParams();
    if (params?.district_id) qs.set("district_id", String(params.district_id));
    if (params?.risk_category) qs.set("risk_category", params.risk_category);
    if (params?.paradox_only) qs.set("paradox_only", "true");
    if (params?.search) qs.set("search", params.search);
    const s = qs.toString();
    return req<VillageSummary[]>(`/villages/${s ? `?${s}` : ""}`);
  },

  village: (id: number) => req<VillageDetail>(`/villages/${id}`),

  facilities: (districtId?: number) =>
    req<Facility[]>(`/facilities/${districtId ? `?district_id=${districtId}` : ""}`),
  facilityMismatch: (districtId?: number) =>
    req<FacilityMismatch[]>(`/facilities/mismatch${districtId ? `?district_id=${districtId}` : ""}`),

  riskList: (params?: { risk_category?: string; district_id?: number }) => {
    const qs = new URLSearchParams();
    if (params?.risk_category) qs.set("risk_category", params.risk_category);
    if (params?.district_id) qs.set("district_id", String(params.district_id));
    const s = qs.toString();
    return req<RiskPrediction[]>(`/risk/${s ? `?${s}` : ""}`);
  },
  prediction: (villageId: number) => req<RiskPrediction>(`/predictions/${villageId}`),
  explanation: (villageId: number) => req<Explanation>(`/explanations/${villageId}`),

  priorities: (params?: { district_id?: number; tier?: string }) => {
    const qs = new URLSearchParams();
    if (params?.district_id) qs.set("district_id", String(params.district_id));
    if (params?.tier) qs.set("tier", params.tier);
    const s = qs.toString();
    return req<Priority[]>(`/priorities/${s ? `?${s}` : ""}`);
  },

  interventions: (villageId: number) => req<InterventionOption[]>(`/interventions/${villageId}`),

  simulate: (payload: SimulationRequest) =>
    req<SimulationResult>("/simulation/", { method: "POST", body: JSON.stringify(payload) }),
  simulationHistory: (villageId: number) => req<SimulationResult[]>(`/simulation/${villageId}/history`),

  optimizeResources: (pool: ResourcePoolIn) =>
    req<ResourceOptimizationResult>("/resources/optimize", { method: "POST", body: JSON.stringify(pool) }),

  earlyWarnings: (indicator: string, districtId?: number) => {
    const qs = new URLSearchParams({ indicator });
    if (districtId) qs.set("district_id", String(districtId));
    return req<EarlyWarning[]>(`/early-warning/?${qs.toString()}`);
  },

  datasets: () => req<DatasetMetadata[]>("/data/datasets"),
  uploadDataset: (sourceName: string, file: File) => {
    const form = new FormData();
    form.set("source_name", sourceName);
    form.set("file", file);
    return req<UploadResponse>("/data/upload", { method: "POST", body: form });
  },
  recompute: () => req<{ message: string }>("/data/recompute", { method: "POST" }),

  methodology: () => req<Record<string, any>>("/methodology/"),
};
