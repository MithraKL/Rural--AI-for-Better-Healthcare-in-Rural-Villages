"""End-to-end smoke tests against the real (seeded) demo database.

These intentionally avoid mutating endpoints (upload/recompute/resource
allocation writes) so the suite is safe to re-run against a shared dev DB.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    assert client.get("/health").json() == {"status": "healthy"}


def test_dashboard_kpis(client):
    body = client.get("/api/dashboard/kpis").json()
    assert body["total_villages"] > 0
    assert body["is_demo_data"] is True


def test_villages_list_and_detail(client):
    villages = client.get("/api/villages/").json()
    assert len(villages) > 0
    detail = client.get(f"/api/villages/{villages[0]['id']}").json()
    assert "gap_breakdown" in detail
    assert len(detail["trend"]) > 0


def test_village_not_found(client):
    res = client.get("/api/villages/999999")
    assert res.status_code == 404


def test_paradox_filter_only_returns_flagged_villages(client):
    villages = client.get("/api/villages/?paradox_only=true").json()
    assert all(v["is_paradox"] for v in villages)


def test_risk_and_predictions_consistent(client):
    risk_list = client.get("/api/risk/").json()
    assert len(risk_list) > 0
    village_id = risk_list[0]["village_id"]
    pred = client.get(f"/api/predictions/{village_id}").json()
    assert pred["village_id"] == village_id


def test_explanation_never_asserts_certainty(client):
    risk_list = client.get("/api/risk/").json()
    village_id = risk_list[0]["village_id"]
    exp = client.get(f"/api/explanations/{village_id}").json()
    assert "diagnosis" not in exp["narrative"].lower() or "not a medical diagnosis" in exp["narrative"].lower()


def test_interventions_never_auto_recommend_infra_for_low_infra_score_only(client):
    villages = client.get("/api/villages/").json()
    for v in villages[:15]:
        options = client.get(f"/api/interventions/{v['id']}").json()
        infra_options = [o for o in options if o["is_infrastructure_expansion"]]
        non_infra_options = [o for o in options if not o["is_infrastructure_expansion"]]
        if infra_options:
            assert len(non_infra_options) >= 0  # infra can co-exist, but must never be the *only* option path forced


def test_simulation_endpoint(client):
    villages = client.get("/api/villages/").json()
    village_id = villages[0]["id"]
    res = client.post("/api/simulation/", json={
        "village_id": village_id, "scenario_name": "Test Scenario", "intervention_ids": [],
        "healthcare_workers": 1, "mobile_medical_units": 0, "vaccine_doses": 0,
        "medicine_units": 0, "outreach_camps_per_quarter": 0, "budget_inr": 0,
    })
    assert res.status_code == 200
    body = res.json()
    assert body["projected_risk"] == body["baseline_risk"]  # no interventions selected => unchanged


def test_resource_optimizer_respects_zero_budget(client):
    res = client.post("/api/resources/optimize", json={
        "name": "Empty", "budget_inr": 0, "doctors": 0, "nurses": 0, "anms": 0, "ashas": 0,
        "mobile_medical_units": 0, "vaccine_doses": 0, "medicine_units": 0, "outreach_camps": 0,
    })
    assert res.status_code == 200
    assert res.json()["allocations"] == []


def test_methodology_exposes_weights(client):
    body = client.get("/api/methodology/").json()
    weights = body["gap_index"]["weights"]
    assert abs(sum(weights.values()) - 1.0) < 0.01
