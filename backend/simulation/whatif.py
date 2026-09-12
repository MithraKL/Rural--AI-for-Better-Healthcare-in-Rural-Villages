"""Module 7 — What-If Impact Simulator.

Deterministic (non-LLM, non-black-box) simulation of the projected effect of
selecting one or more interventions plus a resource "dosage" (workers, MMUs,
vaccine doses, medicine units, outreach frequency, budget) on a village's
risk, utilization and immunization indicators.

Method (fully disclosed on the Methodology page):
1. Each selected intervention contributes an effect size = its catalog
   expected_impact_score / 100.
2. Effects combine with diminishing returns (independent-probability
   combination: 1 - prod(1 - effect_i)), so stacking many interventions
   never mechanically exceeds 100% combined effect.
3. A funding/dosage multiplier scales the combined effect down when the
   allocated budget/resources fall short of the interventions' estimated
   requirement, and slightly up (capped) when resources exceed it.
4. The multiplier-adjusted combined effect closes a fraction of the gap
   between the current value and a realistic ceiling for each metric.

All outputs are explicitly labelled as model-estimated / projected —
never presented as guaranteed outcomes.
"""
from dataclasses import dataclass

RISK_MAX_REDUCTION_FRACTION = 0.65   # combined_effect=1 closes at most 65% of current risk
UTILIZATION_CEILING = 95.0
IMMUNIZATION_CEILING = 96.0


@dataclass
class BaselineMetrics:
    risk: float
    utilization_pct: float
    immunization_pct: float


@dataclass
class SelectedIntervention:
    name: str
    category: str
    cost_estimate_inr: float
    time_months: float
    expected_impact_score: float
    coverage_population: int


@dataclass
class ResourceDosage:
    healthcare_workers: int = 0
    mobile_medical_units: int = 0
    vaccine_doses: int = 0
    medicine_units: int = 0
    outreach_camps_per_quarter: int = 0
    budget_inr: float = 0.0


@dataclass
class SimulationOutput:
    combined_effect: float
    dosage_multiplier: float
    projected_risk: float
    projected_utilization_pct: float
    projected_immunization_pct: float
    cost_estimate_inr: float
    time_months: float
    population_covered: int


def _funding_ratio(dosage: ResourceDosage, required_cost: float) -> float:
    if required_cost <= 0:
        return 1.0
    if dosage.budget_inr <= 0:
        return 1.0  # no explicit budget entered => assume interventions are fully funded as costed
    return max(0.3, min(dosage.budget_inr / required_cost, 2.0))


def _resource_bonus(dosage: ResourceDosage, interventions: list[SelectedIntervention]) -> float:
    categories = {i.category for i in interventions}
    bonus = 0.0
    if "mmu" in categories:
        bonus += min(dosage.mobile_medical_units / 2.0, 1.0) * 0.06
    if "outreach" in categories or "nutrition" in categories:
        bonus += min(dosage.healthcare_workers / 4.0, 1.0) * 0.05
        bonus += min(dosage.outreach_camps_per_quarter / 3.0, 1.0) * 0.05
    if "outreach" in categories:
        bonus += min(dosage.vaccine_doses / 1000.0, 1.0) * 0.05
    if "medicine" in categories:
        bonus += min(dosage.medicine_units / 300.0, 1.0) * 0.08
    return min(bonus, 0.2)


def simulate(baseline: BaselineMetrics, interventions: list[SelectedIntervention], dosage: ResourceDosage) -> SimulationOutput:
    if not interventions:
        return SimulationOutput(
            combined_effect=0.0, dosage_multiplier=1.0,
            projected_risk=baseline.risk, projected_utilization_pct=baseline.utilization_pct,
            projected_immunization_pct=baseline.immunization_pct,
            cost_estimate_inr=0.0, time_months=0.0, population_covered=0,
        )

    combined_effect = 1.0
    for i in interventions:
        combined_effect *= (1 - i.expected_impact_score / 100.0)
    combined_effect = 1 - combined_effect  # 0-1

    required_cost = sum(i.cost_estimate_inr for i in interventions)
    funding_ratio = _funding_ratio(dosage, required_cost)
    bonus = _resource_bonus(dosage, interventions)
    dosage_multiplier = max(0.3, min(funding_ratio, 1.3)) + bonus
    dosage_multiplier = max(0.3, min(dosage_multiplier, 1.5))

    effective_effect = min(combined_effect * dosage_multiplier, 1.0)

    projected_risk = max(baseline.risk - effective_effect * baseline.risk * RISK_MAX_REDUCTION_FRACTION, 5.0)
    projected_utilization = min(
        baseline.utilization_pct + effective_effect * (UTILIZATION_CEILING - baseline.utilization_pct),
        UTILIZATION_CEILING,
    )
    projected_immunization = min(
        baseline.immunization_pct + effective_effect * (IMMUNIZATION_CEILING - baseline.immunization_pct),
        IMMUNIZATION_CEILING,
    )

    return SimulationOutput(
        combined_effect=round(combined_effect, 3),
        dosage_multiplier=round(dosage_multiplier, 2),
        projected_risk=round(projected_risk, 1),
        projected_utilization_pct=round(projected_utilization, 1),
        projected_immunization_pct=round(projected_immunization, 1),
        cost_estimate_inr=round(required_cost, -2),
        time_months=max((i.time_months for i in interventions), default=0.0),
        population_covered=max((i.coverage_population for i in interventions), default=0),
    )
