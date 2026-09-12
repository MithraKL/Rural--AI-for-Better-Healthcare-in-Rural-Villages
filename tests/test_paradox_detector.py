from backend.services.gap_index import GapIndexResult
from backend.services.paradox_detector import detect_paradox


def _scores(**overrides) -> GapIndexResult:
    defaults = dict(
        infrastructure_score=80, workforce_score=70, service_score=70, utilization_score=70,
        outcome_score=70, nutrition_score=70, accessibility_score=70, overall_gap_score=30,
        risk_category="LOW",
    )
    defaults.update(overrides)
    return GapIndexResult(**defaults)


def test_high_infra_low_utilization_and_outcomes_flags_paradox():
    scores = _scores(infrastructure_score=86, service_score=44, utilization_score=32, outcome_score=45)
    result = detect_paradox(scores)
    assert result.is_paradox is True
    assert "infrastructure" in result.note.lower()
    assert "requires field validation" in result.note.lower()


def test_low_infra_never_flags_paradox_even_with_poor_service():
    scores = _scores(infrastructure_score=20, service_score=20, utilization_score=20)
    result = detect_paradox(scores)
    assert result.is_paradox is False
    assert result.note is None


def test_high_infra_with_good_everything_else_is_not_paradox():
    scores = _scores(infrastructure_score=90, service_score=85, utilization_score=80, outcome_score=85)
    result = detect_paradox(scores)
    assert result.is_paradox is False
