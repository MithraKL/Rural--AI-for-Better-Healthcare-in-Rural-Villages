export interface District {
  id: number;
  name: string;
  state_name: string;
  population: number | null;
}

export interface Facility {
  id: number;
  name: string;
  facility_type: string;
  village_id: number | null;
  latitude: number | null;
  longitude: number | null;
  doctors_sanctioned: number;
  doctors_in_position: number;
  nurses_sanctioned: number;
  nurses_in_position: number;
  beds: number;
  monthly_patient_capacity: number;
  has_medicine_stock: number;
}

export interface GapScore {
  quarter: string;
  infrastructure_score: number;
  workforce_score: number;
  service_score: number;
  utilization_score: number;
  outcome_score: number;
  nutrition_score: number;
  accessibility_score: number;
  overall_gap_score: number;
  risk_category: RiskCategory;
  is_paradox: boolean;
  paradox_note: string | null;
}

export type RiskCategory = "CRITICAL" | "HIGH" | "MODERATE" | "LOW";

export interface VillageSummary {
  id: number;
  name: string;
  district_name: string;
  block_name: string;
  state_name: string;
  population: number;
  latitude: number | null;
  longitude: number | null;
  is_demo: boolean;
  overall_gap_score: number | null;
  risk_category: RiskCategory | null;
  is_paradox: boolean | null;
  priority_tier: string | null;
}

export interface VillageDetail extends VillageSummary {
  gap_breakdown: GapScore | null;
  trend: GapScore[];
  facilities: Facility[];
}

export interface RiskFactor {
  factor_name: string;
  contribution_pct: number;
  direction: "increases" | "decreases";
}

export interface RiskPrediction {
  village_id: number;
  quarter: string;
  current_risk: number;
  predicted_risk: number;
  prediction_horizon: string;
  risk_category: RiskCategory;
  confidence: number;
  trend_direction: "improving" | "worsening" | "stable";
  insufficient_data: boolean;
  factors: RiskFactor[];
}

export interface Explanation {
  village_id: number;
  village_name: string;
  headline: string;
  narrative: string;
  drivers: RiskFactor[];
  is_paradox: boolean;
  generated_by: string;
}

export interface Priority {
  village_id: number;
  village_name: string;
  district_name: string;
  priority_score: number;
  priority_tier: string;
  risk_score: number;
  population_affected: number;
  rank: number;
}

export interface InterventionOption {
  id: number;
  problem_tag: string;
  intervention_name: string;
  category: string;
  cost_level: "LOW" | "MEDIUM" | "HIGH";
  cost_estimate_inr: number;
  time_months: number;
  expected_impact_score: number;
  impact_per_resource: number;
  coverage_population: number;
  is_infrastructure_expansion: boolean;
  rank: number | null;
}

export interface SimulationRequest {
  village_id: number;
  scenario_name: string;
  intervention_ids: number[];
  healthcare_workers: number;
  mobile_medical_units: number;
  vaccine_doses: number;
  medicine_units: number;
  outreach_camps_per_quarter: number;
  budget_inr: number;
}

export interface SimulationResult {
  village_id: number;
  scenario_name: string;
  baseline_risk: number;
  projected_risk: number;
  baseline_utilization_pct: number;
  projected_utilization_pct: number;
  baseline_immunization_pct: number;
  projected_immunization_pct: number;
  cost_estimate_inr: number;
  time_months: number;
  population_covered: number;
  disclaimer: string;
}

export interface ResourcePoolIn {
  name: string;
  budget_inr: number;
  doctors: number;
  nurses: number;
  anms: number;
  ashas: number;
  mobile_medical_units: number;
  vaccine_doses: number;
  medicine_units: number;
  outreach_camps: number;
}

export interface ResourceAllocation {
  village_id: number;
  village_name: string;
  intervention_name: string | null;
  allocated_budget_inr: number;
  allocated_mmus: number;
  allocated_vaccine_doses: number;
  allocated_medicine_units: number;
  allocated_workers: number;
  expected_impact_score: number;
  population_covered: number;
  rank: number;
}

export interface ResourceOptimizationResult {
  pool: ResourcePoolIn;
  allocations: ResourceAllocation[];
  remaining_budget_inr: number;
  remaining_mmus: number;
  remaining_vaccine_doses: number;
  remaining_medicine_units: number;
  total_expected_impact: number;
  total_population_covered: number;
}

export interface FacilityMismatch {
  facility_id: number;
  facility_name: string;
  facility_type: string;
  village_name: string | null;
  doctors_in_position: number;
  utilization_pct: number | null;
  mismatch_type: "OVERLOADED" | "UNDER_RESOURCED" | "UNDERUTILIZED" | "BALANCED";
  note: string;
}

export interface EarlyWarning {
  village_id: number;
  village_name: string;
  indicator: string;
  trend_values: number[];
  quarters: string[];
  direction: string;
  message: string;
  periods_to_threshold: number | null;
}

export interface DatasetMetadata {
  id: number;
  source_name: string;
  file_name: string | null;
  granularity: string;
  row_count: number;
  is_demo: boolean;
  uploaded_at: string;
  notes: string | null;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  dataset: DatasetMetadata | null;
  errors: string[];
}

export interface DashboardKPIs {
  critical_villages: number;
  emerging_risk_villages: number;
  at_risk_population: number;
  high_risk_facilities: number;
  total_villages: number;
  resource_utilization_pct: number;
  potential_impact_score: number;
  is_demo_data: boolean;
  quarter: string;
}
