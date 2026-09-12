"""Module 8 — Resource Allocation Optimizer.

A transparent greedy-knapsack heuristic (documented as such — not an exact
LP solver) that allocates a limited, admin-defined resource pool (budget,
workers, MMUs, vaccine doses, medicine units) across villages to maximize
expected aggregate health impact.

Method:
1. Each village contributes its single best-ranked intervention option
   (highest impact-per-resource) as a candidate.
2. Candidates are sorted by a blended greedy score = priority_score x
   impact_per_resource, so the optimizer favors villages that both need help
   most AND offer the best return on limited resources.
3. Candidates are allocated in that order as long as every resource type
   they require is still available; otherwise they are skipped (their
   resources stay reserved for the next affordable candidate).

This is a heuristic, not a global optimum — appropriate for a fast,
explainable planning tool.
"""
from dataclasses import dataclass, field

VACCINE_DOSES_PER_CAPITA = 0.3
MEDICINE_UNITS_PER_CAPITA = 0.4
MEDICINE_UNITS_CAP = 500
VACCINE_DOSES_CAP = 3000


@dataclass
class OptimizerCandidate:
    village_id: int
    village_name: str
    priority_score: float
    population: int
    intervention_name: str
    category: str
    problem_tag: str
    cost_estimate_inr: float
    expected_impact_score: float
    impact_per_resource: float
    coverage_population: int


@dataclass
class ResourcePoolState:
    budget_inr: float = 0.0
    doctors: int = 0
    nurses: int = 0
    anms: int = 0
    ashas: int = 0
    mobile_medical_units: int = 0
    vaccine_doses: int = 0
    medicine_units: int = 0
    outreach_camps: int = 0


@dataclass
class Allocation:
    village_id: int
    village_name: str
    intervention_name: str
    allocated_budget_inr: float
    allocated_mmus: int
    allocated_vaccine_doses: int
    allocated_medicine_units: int
    allocated_workers: int
    expected_impact_score: float
    population_covered: int
    rank: int = 0


def _required_units(c: OptimizerCandidate):
    """Returns (mmus, vaccine_doses, medicine_units, field_workers, doctors) required."""
    mmus = 1 if c.category == "mmu" else 0
    vaccine_doses = min(int(c.coverage_population * VACCINE_DOSES_PER_CAPITA), VACCINE_DOSES_CAP) \
        if c.problem_tag == "LOW_IMMUNIZATION" else 0
    medicine_units = min(int(c.coverage_population * MEDICINE_UNITS_PER_CAPITA), MEDICINE_UNITS_CAP) \
        if c.category == "medicine" else 0
    field_workers = 1 if c.category in ("outreach", "nutrition") else 0
    doctors = 1 if c.category == "staffing" else 0
    return mmus, vaccine_doses, medicine_units, field_workers, doctors


def optimize(pool: ResourcePoolState, candidates: list[OptimizerCandidate]) -> tuple[list[Allocation], ResourcePoolState]:
    remaining = ResourcePoolState(**pool.__dict__)
    field_worker_pool = remaining.nurses + remaining.anms + remaining.ashas
    doctor_pool = remaining.doctors

    ordered = sorted(candidates, key=lambda c: c.priority_score * max(c.impact_per_resource, 0.01), reverse=True)

    allocations: list[Allocation] = []
    for c in ordered:
        mmus_req, vax_req, med_req, worker_req, doctor_req = _required_units(c)

        if c.cost_estimate_inr > remaining.budget_inr:
            continue
        if mmus_req > remaining.mobile_medical_units:
            continue
        if vax_req > remaining.vaccine_doses:
            continue
        if med_req > remaining.medicine_units:
            continue
        if worker_req > field_worker_pool:
            continue
        if doctor_req > doctor_pool:
            continue

        remaining.budget_inr -= c.cost_estimate_inr
        remaining.mobile_medical_units -= mmus_req
        remaining.vaccine_doses -= vax_req
        remaining.medicine_units -= med_req
        field_worker_pool -= worker_req
        doctor_pool -= doctor_req

        allocations.append(Allocation(
            village_id=c.village_id, village_name=c.village_name, intervention_name=c.intervention_name,
            allocated_budget_inr=c.cost_estimate_inr, allocated_mmus=mmus_req,
            allocated_vaccine_doses=vax_req, allocated_medicine_units=med_req,
            allocated_workers=worker_req + doctor_req,
            expected_impact_score=c.expected_impact_score, population_covered=c.coverage_population,
        ))

    for idx, a in enumerate(allocations, start=1):
        a.rank = idx

    return allocations, remaining
