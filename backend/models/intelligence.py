"""Derived / AI-layer tables: everything computed on top of the raw metric
sources above. These are the outputs of the gap index, ML risk model,
prioritization, intervention engine, optimizer and simulator.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class GapScore(Base):
    """Multi-dimensional Healthcare Gap Index for a village at a given quarter."""
    __tablename__ = "gap_scores"

    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False, index=True)
    quarter = Column(String(10), nullable=False, index=True)

    infrastructure_score = Column(Float, nullable=False)
    workforce_score = Column(Float, nullable=False)
    service_score = Column(Float, nullable=False)
    utilization_score = Column(Float, nullable=False)
    outcome_score = Column(Float, nullable=False)
    nutrition_score = Column(Float, nullable=False)
    accessibility_score = Column(Float, nullable=False)

    overall_gap_score = Column(Float, nullable=False)  # 0-100, higher = bigger gap/risk
    risk_category = Column(String(20), nullable=False)  # LOW / MODERATE / HIGH / CRITICAL

    is_paradox = Column(Boolean, default=False)  # Infrastructure-Outcome Paradox flag
    paradox_note = Column(Text, nullable=True)

    computed_at = Column(DateTime, default=datetime.utcnow)


class RiskPrediction(Base):
    """ML-generated forward-looking risk prediction for a village."""
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False, index=True)
    quarter = Column(String(10), nullable=False, index=True)  # quarter the prediction was made from

    current_risk = Column(Float, nullable=False)
    predicted_risk = Column(Float, nullable=False)
    prediction_horizon = Column(String(30), default="next quarter")
    risk_category = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)  # 0-1
    model_name = Column(String(50), default="RandomForestRegressor")
    trend_direction = Column(String(20), default="stable")  # improving / worsening / stable

    insufficient_data = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    factors = relationship("RiskFactor", backref="prediction", cascade="all, delete-orphan")


class RiskFactor(Base):
    """Feature-importance-based explanation for one RiskPrediction ('WHY?')."""
    __tablename__ = "risk_factors"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("risk_predictions.id"), nullable=False, index=True)
    factor_name = Column(String(100), nullable=False)
    contribution_pct = Column(Float, nullable=False)
    direction = Column(String(10), default="increases")  # increases / decreases risk


class PriorityScore(Base):
    """Village prioritization combining risk, population, severity, trend."""
    __tablename__ = "priority_scores"

    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False, index=True)
    quarter = Column(String(10), nullable=False, index=True)

    priority_score = Column(Float, nullable=False)
    priority_tier = Column(String(20), nullable=False)  # CRITICAL / HIGH / MODERATE / LOW
    population_affected = Column(Integer, nullable=False)
    rank = Column(Integer, nullable=True)


class InterventionOption(Base):
    """A candidate intervention generated for a village's detected problems."""
    __tablename__ = "intervention_options"

    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False, index=True)
    quarter = Column(String(10), nullable=False, index=True)

    problem_tag = Column(String(50), nullable=False)  # e.g. LOW_IMMUNIZATION
    intervention_name = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)  # outreach / staffing / medicine / infrastructure / mmu

    cost_level = Column(String(10), nullable=False)  # LOW / MEDIUM / HIGH
    cost_estimate_inr = Column(Float, nullable=False)
    time_months = Column(Float, nullable=False)
    expected_impact_score = Column(Float, nullable=False)  # 0-100 model-estimated
    impact_per_resource = Column(Float, nullable=False)  # expected_impact / cost (x1000 scaling)
    coverage_population = Column(Integer, nullable=False)

    is_infrastructure_expansion = Column(Boolean, default=False)
    rank = Column(Integer, nullable=True)


class ResourcePool(Base):
    """Admin-defined available resources for one planning session."""
    __tablename__ = "resource_pools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), default="Default Planning Session")
    budget_inr = Column(Float, default=0.0)
    doctors = Column(Integer, default=0)
    nurses = Column(Integer, default=0)
    anms = Column(Integer, default=0)
    ashas = Column(Integer, default=0)
    mobile_medical_units = Column(Integer, default=0)
    vaccine_doses = Column(Integer, default=0)
    medicine_units = Column(Integer, default=0)
    outreach_camps = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class ResourceAllocation(Base):
    """Result of running the resource optimizer against a ResourcePool."""
    __tablename__ = "resource_allocations"

    id = Column(Integer, primary_key=True, index=True)
    pool_id = Column(Integer, ForeignKey("resource_pools.id"), nullable=False, index=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False, index=True)
    intervention_option_id = Column(Integer, ForeignKey("intervention_options.id"), nullable=True)

    allocated_budget_inr = Column(Float, default=0.0)
    allocated_mmus = Column(Integer, default=0)
    allocated_vaccine_doses = Column(Integer, default=0)
    allocated_medicine_units = Column(Integer, default=0)
    allocated_workers = Column(Integer, default=0)

    expected_impact_score = Column(Float, default=0.0)
    population_covered = Column(Integer, default=0)
    rank = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SimulationResult(Base):
    """A saved What-If simulation run (for comparison across scenarios)."""
    __tablename__ = "simulation_results"

    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False, index=True)
    scenario_name = Column(String(100), nullable=False)

    inputs_json = Column(Text, nullable=False)  # selected interventions + resource dosage

    baseline_risk = Column(Float, nullable=False)
    projected_risk = Column(Float, nullable=False)
    baseline_utilization_pct = Column(Float, nullable=False)
    projected_utilization_pct = Column(Float, nullable=False)
    baseline_immunization_pct = Column(Float, nullable=False)
    projected_immunization_pct = Column(Float, nullable=False)

    cost_estimate_inr = Column(Float, nullable=False)
    time_months = Column(Float, nullable=False)
    population_covered = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


class DatasetMetadata(Base):
    """Metadata for every dataset ingested (uploaded or bundled demo data)."""
    __tablename__ = "dataset_metadata"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(50), nullable=False)  # RHS / HMIS / NFHS / DLHS / AHS / Anganwadi
    file_name = Column(String(255), nullable=True)
    granularity = Column(String(20), nullable=False)  # state/district/block/village/facility
    row_count = Column(Integer, default=0)
    is_demo = Column(Boolean, default=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
