import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Village, GapScore, HMISMetric, InterventionOption, SimulationResult
from backend.schemas import SimulationRequest, SimulationResultOut
from backend.simulation.whatif import BaselineMetrics, SelectedIntervention, ResourceDosage, simulate

router = APIRouter()


@router.post("/", response_model=SimulationResultOut)
def run_simulation(req: SimulationRequest, db: Session = Depends(get_db)):
    village = db.query(Village).filter(Village.id == req.village_id).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    gap = (
        db.query(GapScore).filter(GapScore.village_id == req.village_id)
        .order_by(GapScore.quarter.desc()).first()
    )
    hmis = (
        db.query(HMISMetric).filter(HMISMetric.village_id == req.village_id)
        .order_by(HMISMetric.quarter.desc()).first()
    )
    if not gap or not hmis:
        raise HTTPException(status_code=400, detail="Insufficient historical data for reliable simulation.")

    baseline = BaselineMetrics(
        risk=gap.overall_gap_score, utilization_pct=min(hmis.opd_utilization_pct, 100.0),
        immunization_pct=hmis.full_immunization_pct,
    )

    options = db.query(InterventionOption).filter(InterventionOption.id.in_(req.intervention_ids)).all()
    if req.intervention_ids and not options:
        raise HTTPException(status_code=404, detail="None of the specified intervention IDs were found.")

    interventions = [
        SelectedIntervention(
            name=o.intervention_name, category=o.category, cost_estimate_inr=o.cost_estimate_inr,
            time_months=o.time_months, expected_impact_score=o.expected_impact_score,
            coverage_population=o.coverage_population,
        )
        for o in options
    ]
    dosage = ResourceDosage(
        healthcare_workers=req.healthcare_workers, mobile_medical_units=req.mobile_medical_units,
        vaccine_doses=req.vaccine_doses, medicine_units=req.medicine_units,
        outreach_camps_per_quarter=req.outreach_camps_per_quarter, budget_inr=req.budget_inr,
    )

    result = simulate(baseline, interventions, dosage)

    db.add(SimulationResult(
        village_id=req.village_id, scenario_name=req.scenario_name,
        inputs_json=json.dumps(req.model_dump()),
        baseline_risk=baseline.risk, projected_risk=result.projected_risk,
        baseline_utilization_pct=baseline.utilization_pct, projected_utilization_pct=result.projected_utilization_pct,
        baseline_immunization_pct=baseline.immunization_pct, projected_immunization_pct=result.projected_immunization_pct,
        cost_estimate_inr=result.cost_estimate_inr, time_months=result.time_months,
        population_covered=result.population_covered,
    ))
    db.commit()

    return SimulationResultOut(
        village_id=req.village_id, scenario_name=req.scenario_name,
        baseline_risk=baseline.risk, projected_risk=result.projected_risk,
        baseline_utilization_pct=baseline.utilization_pct, projected_utilization_pct=result.projected_utilization_pct,
        baseline_immunization_pct=baseline.immunization_pct, projected_immunization_pct=result.projected_immunization_pct,
        cost_estimate_inr=result.cost_estimate_inr, time_months=result.time_months,
        population_covered=result.population_covered,
    )


@router.get("/{village_id}/history", response_model=list[SimulationResultOut])
def simulation_history(village_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(SimulationResult).filter(SimulationResult.village_id == village_id)
        .order_by(SimulationResult.created_at.desc()).limit(20).all()
    )
    return [
        SimulationResultOut(
            village_id=r.village_id, scenario_name=r.scenario_name,
            baseline_risk=r.baseline_risk, projected_risk=r.projected_risk,
            baseline_utilization_pct=r.baseline_utilization_pct, projected_utilization_pct=r.projected_utilization_pct,
            baseline_immunization_pct=r.baseline_immunization_pct, projected_immunization_pct=r.projected_immunization_pct,
            cost_estimate_inr=r.cost_estimate_inr, time_months=r.time_months, population_covered=r.population_covered,
        )
        for r in rows
    ]
