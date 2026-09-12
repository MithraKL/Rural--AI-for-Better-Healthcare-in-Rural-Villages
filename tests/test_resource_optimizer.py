from backend.optimization.resource_optimizer import ResourcePoolState, OptimizerCandidate, optimize


def _candidate(**overrides) -> OptimizerCandidate:
    defaults = dict(
        village_id=1, village_name="A", priority_score=50, population=5000,
        intervention_name="Vaccination Outreach Camp", category="outreach", problem_tag="LOW_IMMUNIZATION",
        cost_estimate_inr=50000, expected_impact_score=70, impact_per_resource=100, coverage_population=3000,
    )
    defaults.update(overrides)
    return OptimizerCandidate(**defaults)


def test_allocates_within_budget_and_stops_when_exhausted():
    pool = ResourcePoolState(budget_inr=60000, vaccine_doses=5000, nurses=5, anms=5, ashas=5)
    candidates = [_candidate(village_id=1), _candidate(village_id=2, cost_estimate_inr=50000)]
    allocations, remaining = optimize(pool, candidates)
    assert len(allocations) == 1
    assert remaining.budget_inr == 10000


def test_higher_priority_times_impact_allocated_first():
    pool = ResourcePoolState(budget_inr=50000, vaccine_doses=5000, nurses=5, anms=5, ashas=5)
    low = _candidate(village_id=1, priority_score=10, impact_per_resource=10)
    high = _candidate(village_id=2, priority_score=90, impact_per_resource=90)
    allocations, _ = optimize(pool, [low, high])
    assert allocations[0].village_id == 2


def test_skips_candidate_exceeding_mmu_availability():
    pool = ResourcePoolState(budget_inr=1_000_000, mobile_medical_units=0)
    candidates = [_candidate(category="mmu", cost_estimate_inr=100000)]
    allocations, remaining = optimize(pool, candidates)
    assert len(allocations) == 0
    assert remaining.mobile_medical_units == 0


def test_never_over_allocates_a_resource():
    pool = ResourcePoolState(budget_inr=1_000_000, vaccine_doses=1000)
    candidates = [_candidate(village_id=i, population=10000, coverage_population=10000) for i in range(5)]
    allocations, remaining = optimize(pool, candidates)
    assert remaining.vaccine_doses >= 0
