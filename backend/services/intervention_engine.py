"""Module 5 & 6 — Intervention Recommendation + Optimization.

Maps detected problems to a catalogue of concrete interventions (never
generic advice), estimates cost / time / expected impact for each, and
computes an "impact per resource" score used to rank options.

Design principle (explicit product requirement): the engine must NOT jump
to recommending new infrastructure. An infrastructure-expansion option is
only generated when the Infrastructure dimension itself is genuinely poor
(score < 35) — i.e. after confirming the gap cannot be explained by
under-utilization, staffing, medicines or outreach alone.

All impact figures are labelled as model-estimated / projected, never as
guaranteed real-world results.
"""
from dataclasses import dataclass
from backend.services.gap_index import GapIndexResult

INFRA_GAP_THRESHOLD = 35.0
PROBLEM_THRESHOLD = 45.0
OVERLOAD_UTILIZATION_PCT = 115.0


@dataclass
class InterventionContext:
    population: int
    has_medicine_stock: int
    opd_utilization_pct: float


@dataclass
class InterventionCandidate:
    problem_tag: str
    intervention_name: str
    category: str
    cost_level: str
    cost_estimate_inr: float
    time_months: float
    expected_impact_score: float
    impact_per_resource: float
    coverage_population: int
    is_infrastructure_expansion: bool = False


# (name, category, cost_level, base_cost_inr, time_months, base_impact, coverage_fraction)
CATALOG = {
    "LOW_IMMUNIZATION": [
        ("Vaccination Outreach Camp", "outreach", "LOW", 50_000, 1, 72, 0.75),
        ("Mobile Health Camp", "mmu", "MEDIUM", 250_000, 2, 66, 0.70),
        ("Community Health Worker Outreach", "outreach", "LOW", 40_000, 1, 55, 0.65),
    ],
    "HIGH_MALNUTRITION": [
        ("Nutrition Intervention Program", "nutrition", "LOW", 60_000, 1, 68, 0.70),
        ("Anganwadi Outreach Drive", "nutrition", "LOW", 45_000, 1, 60, 0.65),
        ("Growth Monitoring Camp", "nutrition", "LOW", 35_000, 1, 50, 0.60),
        ("Supplementary Nutrition Support", "nutrition", "MEDIUM", 220_000, 2, 74, 0.80),
    ],
    "LOW_UTILIZATION": [
        ("Community Awareness Campaign", "outreach", "LOW", 40_000, 1, 58, 0.55),
        ("Service-Timing Adjustment", "service", "LOW", 15_000, 1, 40, 0.50),
        ("Mobile Medical Unit Deployment", "mmu", "MEDIUM", 260_000, 3, 78, 0.70),
    ],
    "MEDICINE_SHORTAGE": [
        ("Medicine Replenishment", "medicine", "LOW", 70_000, 1, 75, 0.90),
    ],
    "ACCESSIBILITY_GAP": [
        ("Mobile Medical Unit for Outreach", "mmu", "MEDIUM", 260_000, 3, 76, 0.65),
        ("Outreach Camp Scheduling", "outreach", "LOW", 45_000, 1, 55, 0.55),
        ("Referral & Transport Planning", "service", "LOW", 30_000, 1, 45, 0.40),
    ],
    "FACILITY_OVERLOAD": [
        ("Resource Redistribution Review", "staffing", "MEDIUM", 150_000, 2, 60, 0.50),
        ("Referral Balancing to Nearby Facility", "service", "LOW", 20_000, 1, 50, 0.45),
        ("Additional Outreach Capacity", "outreach", "MEDIUM", 180_000, 2, 55, 0.50),
    ],
    "WORKFORCE_GAP": [
        ("Staff Deputation Request", "staffing", "MEDIUM", 300_000, 3, 65, 0.60),
        ("ANM/ASHA Incentive Outreach Drive", "outreach", "LOW", 50_000, 1, 50, 0.50),
    ],
    "INFRASTRUCTURE_GAP": [
        ("New Sub-Centre / PHC Construction", "infrastructure", "HIGH", 1_500_000, 18, 80, 1.0),
    ],
}


def _impact_per_resource(impact: float, cost_inr: float) -> float:
    return round(impact / max(cost_inr / 100_000.0, 0.1), 2)


def detect_problems(scores: GapIndexResult, ctx: InterventionContext) -> list[str]:
    problems = []
    if scores.service_score <= PROBLEM_THRESHOLD:
        problems.append("LOW_IMMUNIZATION")
    if scores.nutrition_score <= PROBLEM_THRESHOLD:
        problems.append("HIGH_MALNUTRITION")
    if scores.utilization_score <= PROBLEM_THRESHOLD:
        problems.append("LOW_UTILIZATION")
    if not ctx.has_medicine_stock:
        problems.append("MEDICINE_SHORTAGE")
    if scores.accessibility_score <= PROBLEM_THRESHOLD:
        problems.append("ACCESSIBILITY_GAP")
    if ctx.opd_utilization_pct >= OVERLOAD_UTILIZATION_PCT:
        problems.append("FACILITY_OVERLOAD")
    if scores.workforce_score <= PROBLEM_THRESHOLD:
        problems.append("WORKFORCE_GAP")

    # Infrastructure expansion is considered ONLY when infra itself is genuinely
    # poor — never as a first response to utilization/staffing/medicine problems.
    if scores.infrastructure_score < INFRA_GAP_THRESHOLD:
        problems.append("INFRASTRUCTURE_GAP")

    return problems


def generate_interventions(scores: GapIndexResult, ctx: InterventionContext) -> list[InterventionCandidate]:
    problems = detect_problems(scores, ctx)
    candidates: list[InterventionCandidate] = []

    for problem in problems:
        for name, category, cost_level, base_cost, time_months, base_impact, coverage_frac in CATALOG[problem]:
            cost = base_cost * (0.6 + ctx.population / 8000.0)
            coverage = int(ctx.population * coverage_frac)
            candidates.append(InterventionCandidate(
                problem_tag=problem,
                intervention_name=name,
                category=category,
                cost_level=cost_level,
                cost_estimate_inr=round(cost, -2),
                time_months=time_months,
                expected_impact_score=base_impact,
                impact_per_resource=_impact_per_resource(base_impact, cost),
                coverage_population=coverage,
                is_infrastructure_expansion=(problem == "INFRASTRUCTURE_GAP"),
            ))

    candidates.sort(key=lambda c: c.impact_per_resource, reverse=True)
    return candidates


def impact_per_resource_label(value: float) -> str:
    if value >= 8:
        return "VERY HIGH"
    if value >= 4:
        return "HIGH"
    if value >= 1.5:
        return "MEDIUM"
    return "LOW"
