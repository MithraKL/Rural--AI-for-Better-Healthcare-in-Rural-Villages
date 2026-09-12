"""Raw source-of-truth metric tables — one table per data source.

Each table is kept at the geographic granularity its real-world source
actually publishes at (village for Anganwadi/HMIS-aggregated, district for
NFHS/DLHS/AHS). Nothing here is fabricated down to a finer granularity than
the source supports; the `granularity` constant on each model documents this
for the API layer / frontend.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from backend.database import Base


class RHSMetric(Base):
    """Rural Health Statistics — infrastructure & workforce, aggregated per village per quarter."""
    __tablename__ = "rhs_metrics"
    granularity = "village"

    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False, index=True)
    quarter = Column(String(10), nullable=False, index=True)  # e.g. "2024-Q1"

    sub_centres_count = Column(Integer, default=0)
    phc_count = Column(Integer, default=0)
    chc_count = Column(Integer, default=0)
    mmu_count = Column(Integer, default=0)

    doctors_sanctioned = Column(Integer, default=0)
    doctors_in_position = Column(Integer, default=0)
    nurses_sanctioned = Column(Integer, default=0)
    nurses_in_position = Column(Integer, default=0)
    anms_in_position = Column(Integer, default=0)
    ashas_linked = Column(Integer, default=0)

    beds_total = Column(Integer, default=0)
    monthly_capacity_total = Column(Integer, default=0)


class HMISMetric(Base):
    """HMIS — service utilization & delivery, per village per quarter."""
    __tablename__ = "hmis_metrics"
    granularity = "village"

    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False, index=True)
    quarter = Column(String(10), nullable=False, index=True)

    opd_visits = Column(Integer, default=0)
    ipd_admissions = Column(Integer, default=0)
    deliveries = Column(Integer, default=0)
    c_sections = Column(Integer, default=0)
    anc_visits = Column(Integer, default=0)
    immunization_sessions_held = Column(Integer, default=0)
    full_immunization_pct = Column(Float, default=0.0)
    institutional_delivery_pct = Column(Float, default=0.0)
    opd_utilization_pct = Column(Float, default=0.0)  # opd_visits vs facility capacity


class NFHSMetric(Base):
    """NFHS — population health survey, district-level only (do NOT infer to village)."""
    __tablename__ = "nfhs_metrics"
    granularity = "district"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False, index=True)
    round = Column(String(20), nullable=False)  # e.g. "NFHS-5"

    stunting_pct = Column(Float, default=0.0)
    wasting_pct = Column(Float, default=0.0)
    underweight_pct = Column(Float, default=0.0)
    anemia_women_pct = Column(Float, default=0.0)
    anemia_children_pct = Column(Float, default=0.0)
    full_immunization_pct = Column(Float, default=0.0)
    institutional_delivery_pct = Column(Float, default=0.0)
    under5_mortality_rate = Column(Float, default=0.0)


class DLHSMetric(Base):
    """District Level Household Survey — district-level."""
    __tablename__ = "dlhs_metrics"
    granularity = "district"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False, index=True)
    round = Column(String(20), nullable=False)

    institutional_delivery_pct = Column(Float, default=0.0)
    full_immunization_pct = Column(Float, default=0.0)
    contraceptive_prevalence_pct = Column(Float, default=0.0)


class AHSMetric(Base):
    """Annual Health Survey — district-level vital statistics."""
    __tablename__ = "ahs_metrics"
    granularity = "district"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False, index=True)
    year = Column(String(10), nullable=False)

    maternal_mortality_ratio = Column(Float, default=0.0)
    infant_mortality_rate = Column(Float, default=0.0)
    under5_mortality_rate = Column(Float, default=0.0)
    total_fertility_rate = Column(Float, default=0.0)


class AnganwadiMetric(Base):
    """Anganwadi (ICDS) — nutrition & early childhood, per village per quarter."""
    __tablename__ = "anganwadi_metrics"
    granularity = "village"

    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False, index=True)
    quarter = Column(String(10), nullable=False, index=True)

    children_registered = Column(Integer, default=0)
    children_weighed_pct = Column(Float, default=0.0)
    severely_underweight_pct = Column(Float, default=0.0)
    moderately_underweight_pct = Column(Float, default=0.0)
    supplementary_nutrition_days = Column(Integer, default=0)  # out of ~90/quarter
    doctor_visits_count = Column(Integer, default=0)
    growth_monitoring_pct = Column(Float, default=0.0)
    water_availability = Column(Integer, default=1)
    toilet_availability = Column(Integer, default=1)
    medicine_availability_pct = Column(Float, default=0.0)
