from backend.simulation.whatif import BaselineMetrics, SelectedIntervention, ResourceDosage, simulate


def test_no_interventions_returns_baseline_unchanged():
    baseline = BaselineMetrics(risk=70, utilization_pct=30, immunization_pct=40)
    result = simulate(baseline, [], ResourceDosage())
    assert result.projected_risk == baseline.risk
    assert result.combined_effect == 0.0


def test_intervention_reduces_risk_and_raises_utilization():
    baseline = BaselineMetrics(risk=70, utilization_pct=30, immunization_pct=40)
    interventions = [SelectedIntervention(
        name="Vaccination Outreach Camp", category="outreach", cost_estimate_inr=50000,
        time_months=1, expected_impact_score=70, coverage_population=5000,
    )]
    result = simulate(baseline, interventions, ResourceDosage(budget_inr=50000))
    assert result.projected_risk < baseline.risk
    assert result.projected_utilization_pct > baseline.utilization_pct
    assert result.cost_estimate_inr == 50000


def test_underfunding_reduces_effect_versus_full_funding():
    baseline = BaselineMetrics(risk=70, utilization_pct=30, immunization_pct=40)
    interventions = [SelectedIntervention(
        name="Mobile Medical Unit", category="mmu", cost_estimate_inr=260000,
        time_months=3, expected_impact_score=78, coverage_population=7000,
    )]
    fully_funded = simulate(baseline, interventions, ResourceDosage(budget_inr=260000))
    underfunded = simulate(baseline, interventions, ResourceDosage(budget_inr=50000))
    assert underfunded.projected_risk > fully_funded.projected_risk


def test_combined_effect_never_exceeds_one():
    baseline = BaselineMetrics(risk=90, utilization_pct=20, immunization_pct=30)
    interventions = [
        SelectedIntervention(name="A", category="outreach", cost_estimate_inr=10000, time_months=1, expected_impact_score=95, coverage_population=1000),
        SelectedIntervention(name="B", category="mmu", cost_estimate_inr=10000, time_months=1, expected_impact_score=95, coverage_population=1000),
        SelectedIntervention(name="C", category="medicine", cost_estimate_inr=10000, time_months=1, expected_impact_score=95, coverage_population=1000),
    ]
    result = simulate(baseline, interventions, ResourceDosage(budget_inr=30000))
    assert result.combined_effect <= 1.0
    assert result.projected_risk >= 5.0
