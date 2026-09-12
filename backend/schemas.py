from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


# ---------------------------------------------------------------------------
# Geography
# ---------------------------------------------------------------------------
class DistrictOut(BaseModel):
    id: int
    name: str
    state_name: str
    population: Optional[int] = None

    class Config:
        from_attributes = True


class FacilityOut(BaseModel):
    id: int
    name: str
    facility_type: str
    village_id: Optional[int]
    latitude: Optional[float]
    longitude: Optional[float]
    doctors_sanctioned: int
    doctors_in_position: int
    nurses_sanctioned: int
    nurses_in_position: int
    beds: int
    monthly_patient_capacity: int
    has_medicine_stock: int

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Gap Index / Village
# ---------------------------------------------------------------------------
class GapScoreOut(BaseModel):
    quarter: str
    infrastructure_score: float
    workforce_score: float
    service_score: float
    utilization_score: float
    outcome_score: float
    nutrition_score: float
    accessibility_score: float
    overall_gap_score: float
    risk_category: str
    is_paradox: bool
    paradox_note: Optional[str] = None

    class Config:
        from_attributes = True


class VillageSummary(BaseModel):
    id: int
    name: str
    district_name: str
    block_name: str
    state_name: str
    population: int
    latitude: Optional[float]
    longitude: Optional[float]
    is_demo: bool
    overall_gap_score: Optional[float] = None
    risk_category: Optional[str] = None
    is_paradox: Optional[bool] = None
    priority_tier: Optional[str] = None


class VillageDetail(VillageSummary):
    gap_breakdown: Optional[GapScoreOut] = None
    trend: List[GapScoreOut] = []
    facilities: List[FacilityOut] = []


# ---------------------------------------------------------------------------
# Risk / Prediction / Explanation
# ---------------------------------------------------------------------------
class RiskFactorOut(BaseModel):
    factor_name: str
    contribution_pct: float
    direction: str

    class Config:
        from_attributes = True


class RiskPredictionOut(BaseModel):
    village_id: int
    quarter: str
    current_risk: float
    predicted_risk: float
    prediction_horizon: str
    risk_category: str
    confidence: float
    trend_direction: str
    insufficient_data: bool
    factors: List[RiskFactorOut] = []

    class Config:
        from_attributes = True


class ExplanationOut(BaseModel):
    village_id: int
    village_name: str
    headline: str
    narrative: str
    drivers: List[RiskFactorOut]
    is_paradox: bool
    generated_by: str  # "template" | "watsonx"


# ---------------------------------------------------------------------------
# Priority
# ---------------------------------------------------------------------------
class PriorityOut(BaseModel):
    village_id: int
    village_name: str
    district_name: str
    priority_score: float
    priority_tier: str
    risk_score: float
    population_affected: int
    rank: int

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Interventions
# ---------------------------------------------------------------------------
class InterventionOptionOut(BaseModel):
    id: int
    problem_tag: str
    intervention_name: str
    category: str
    cost_level: str
    cost_estimate_inr: float
    time_months: float
    expected_impact_score: float
    impact_per_resource: float
    coverage_population: int
    is_infrastructure_expansion: bool
    rank: Optional[int]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------
class SimulationRequest(BaseModel):
    village_id: int
    scenario_name: str = "Custom Scenario"
    intervention_ids: List[int] = Field(default_factory=list)
    healthcare_workers: int = 0
    mobile_medical_units: int = 0
    vaccine_doses: int = 0
    medicine_units: int = 0
    outreach_camps_per_quarter: int = 0
    budget_inr: float = 0.0


class SimulationResultOut(BaseModel):
    village_id: int
    scenario_name: str
    baseline_risk: float
    projected_risk: float
    baseline_utilization_pct: float
    projected_utilization_pct: float
    baseline_immunization_pct: float
    projected_immunization_pct: float
    cost_estimate_inr: float
    time_months: float
    population_covered: int
    disclaimer: str = "Model-estimated / projected impact — requires field validation. Not a guaranteed outcome."


# ---------------------------------------------------------------------------
# Resource Optimization
# ---------------------------------------------------------------------------
class ResourcePoolIn(BaseModel):
    name: str = "Planning Session"
    budget_inr: float = 0.0
    doctors: int = 0
    nurses: int = 0
    anms: int = 0
    ashas: int = 0
    mobile_medical_units: int = 0
    vaccine_doses: int = 0
    medicine_units: int = 0
    outreach_camps: int = 0


class ResourceAllocationOut(BaseModel):
    village_id: int
    village_name: str
    intervention_name: Optional[str]
    allocated_budget_inr: float
    allocated_mmus: int
    allocated_vaccine_doses: int
    allocated_medicine_units: int
    allocated_workers: int
    expected_impact_score: float
    population_covered: int
    rank: int


class ResourceOptimizationResult(BaseModel):
    pool: ResourcePoolIn
    allocations: List[ResourceAllocationOut]
    remaining_budget_inr: float
    remaining_mmus: int
    remaining_vaccine_doses: int
    remaining_medicine_units: int
    total_expected_impact: float
    total_population_covered: int


# ---------------------------------------------------------------------------
# Resource wastage / mismatch
# ---------------------------------------------------------------------------
class FacilityMismatchOut(BaseModel):
    facility_id: int
    facility_name: str
    facility_type: str
    village_name: Optional[str]
    doctors_in_position: int
    utilization_pct: Optional[float]
    mismatch_type: str  # OVERLOADED / UNDERUTILIZED / UNDER_RESOURCED / BALANCED
    note: str


# ---------------------------------------------------------------------------
# Early warning
# ---------------------------------------------------------------------------
class EarlyWarningOut(BaseModel):
    village_id: int
    village_name: str
    indicator: str
    trend_values: List[float]
    quarters: List[str]
    direction: str  # worsening / improving / stable
    message: str
    periods_to_threshold: Optional[int] = None


# ---------------------------------------------------------------------------
# Data ingestion
# ---------------------------------------------------------------------------
class DatasetMetadataOut(BaseModel):
    id: int
    source_name: str
    file_name: Optional[str]
    granularity: str
    row_count: int
    is_demo: bool
    uploaded_at: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    success: bool
    message: str
    dataset: Optional[DatasetMetadataOut] = None
    errors: List[str] = []


# ---------------------------------------------------------------------------
# Dashboard KPIs
# ---------------------------------------------------------------------------
class DashboardKPIs(BaseModel):
    critical_villages: int
    emerging_risk_villages: int
    at_risk_population: int
    high_risk_facilities: int
    total_villages: int
    resource_utilization_pct: float
    potential_impact_score: float
    is_demo_data: bool
    quarter: str
