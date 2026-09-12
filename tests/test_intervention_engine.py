from backend.services.gap_index import GapIndexResult
from backend.services.intervention_engine import InterventionContext, generate_interventions, detect_problems


def _scores(**overrides) -> GapIndexResult:
    defaults = dict(
        infrastructure_score=70, workforce_score=70, service_score=70, utilization_score=70,
        outcome_score=70, nutrition_score=70, accessibility_score=70, overall_gap_score=30,
        risk_category="LOW",
    )
    defaults.update(overrides)
    return GapIndexResult(**defaults)


def test_low_utilization_never_recommends_infrastructure_first():
    scores = _scores(utilization_score=20, infrastructure_score=70)
    ctx = InterventionContext(population=5000, has_medicine_stock=1, opd_utilization_pct=20)
    candidates = generate_interventions(scores, ctx)
    assert len(candidates) > 0
    assert not any(c.is_infrastructure_expansion for c in candidates)


def test_genuinely_poor_infrastructure_does_get_an_expansion_option():
    scores = _scores(infrastructure_score=20)
    ctx = InterventionContext(population=5000, has_medicine_stock=1, opd_utilization_pct=70)
    candidates = generate_interventions(scores, ctx)
    assert any(c.is_infrastructure_expansion for c in candidates)


def test_medicine_shortage_detected_when_stock_missing():
    scores = _scores()
    ctx = InterventionContext(population=5000, has_medicine_stock=0, opd_utilization_pct=70)
    problems = detect_problems(scores, ctx)
    assert "MEDICINE_SHORTAGE" in problems


def test_candidates_ranked_by_impact_per_resource_descending():
    scores = _scores(utilization_score=20, nutrition_score=20)
    ctx = InterventionContext(population=5000, has_medicine_stock=1, opd_utilization_pct=20)
    candidates = generate_interventions(scores, ctx)
    ratios = [c.impact_per_resource for c in candidates]
    assert ratios == sorted(ratios, reverse=True)
