from backend.services.gap_index import GapIndexInput, compute_gap_index


def _base_input(**overrides) -> GapIndexInput:
    defaults = dict(
        population=5000,
        sub_centres_count=1, phc_count=0, monthly_capacity_total=250, mmu_count=0,
        doctors_sanctioned=1, doctors_in_position=1, nurses_sanctioned=2, nurses_in_position=2,
        anms_in_position=2, ashas_linked=5,
        institutional_delivery_pct=80, full_immunization_pct=80, immunization_sessions_held=4,
        opd_utilization_pct=70,
        district_under5_mortality_rate=35,
        severely_underweight_pct=5, moderately_underweight_pct=10,
        growth_monitoring_pct=80, supplementary_nutrition_days=80,
        distance_to_facility_km=2, has_all_weather_road=1,
    )
    defaults.update(overrides)
    return GapIndexInput(**defaults)


def test_healthy_village_scores_low_risk():
    result = compute_gap_index(_base_input())
    assert result.overall_gap_score < 35
    assert result.risk_category == "LOW"


def test_poor_indicators_score_high_risk():
    result = compute_gap_index(_base_input(
        doctors_in_position=0, institutional_delivery_pct=20, full_immunization_pct=20,
        opd_utilization_pct=10, severely_underweight_pct=35, moderately_underweight_pct=20,
        growth_monitoring_pct=20, distance_to_facility_km=18, has_all_weather_road=0,
        sub_centres_count=0, monthly_capacity_total=20,
    ))
    assert result.overall_gap_score > 55
    assert result.risk_category in ("HIGH", "CRITICAL")


def test_scores_bounded_between_0_and_100():
    result = compute_gap_index(_base_input())
    for value in result.as_dict().values():
        if isinstance(value, float):
            assert 0 <= value <= 100
