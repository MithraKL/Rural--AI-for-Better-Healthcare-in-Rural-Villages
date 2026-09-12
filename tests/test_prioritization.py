from backend.services.prioritization import PriorityInput, compute_priorities


def test_higher_risk_and_population_ranks_first():
    inputs = [
        PriorityInput(village_id=1, predicted_risk=90, overall_gap_score=85, population=10000, trend_delta=5),
        PriorityInput(village_id=2, predicted_risk=40, overall_gap_score=35, population=1000, trend_delta=0),
    ]
    results = compute_priorities(inputs)
    assert results[0].village_id == 1
    assert results[0].rank == 1
    assert results[0].priority_score > results[1].priority_score


def test_empty_input_returns_empty_list():
    assert compute_priorities([]) == []


def test_population_affected_passed_through():
    inputs = [PriorityInput(village_id=5, predicted_risk=60, overall_gap_score=50, population=4200, trend_delta=2)]
    results = compute_priorities(inputs)
    assert results[0].population_affected == 4200
