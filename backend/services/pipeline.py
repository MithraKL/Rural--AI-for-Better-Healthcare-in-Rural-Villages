"""Orchestrates the full decision-intelligence pipeline end-to-end:

DATA -> GAP INDEX -> PARADOX DETECTION -> ML RISK PREDICTION -> EXPLAINABILITY
-> PRIORITIZATION -> INTERVENTION RECOMMENDATION

Run once at startup/seed time, and re-run (via POST /api/data/recompute)
whenever new data is ingested.
"""
import logging
from sqlalchemy.orm import Session

from backend.models import (
    Village, District, Facility, RHSMetric, HMISMetric, AnganwadiMetric, AHSMetric, NFHSMetric,
    GapScore, RiskPrediction, RiskFactor, PriorityScore, InterventionOption,
)
from backend.services.gap_index import GapIndexInput, compute_gap_index
from backend.services.paradox_detector import detect_paradox
from backend.services.prioritization import PriorityInput, compute_priorities
from backend.services.intervention_engine import InterventionContext, generate_interventions
from backend.ml.risk_model import train_risk_model, predict_next_quarter
from backend.ml.explainability import explain_prediction

logger = logging.getLogger(__name__)


def _clear_derived_tables(db: Session):
    db.query(RiskFactor).delete()
    db.query(RiskPrediction).delete()
    db.query(PriorityScore).delete()
    db.query(InterventionOption).delete()
    db.query(GapScore).delete()
    db.commit()


def recompute_all(db: Session) -> dict:
    _clear_derived_tables(db)

    villages = db.query(Village).all()
    district_ahs = {a.district_id: a for a in db.query(AHSMetric).all()}

    village_histories: dict[int, list[dict]] = {}

    for village in villages:
        rhs_rows = {r.quarter: r for r in db.query(RHSMetric).filter(RHSMetric.village_id == village.id).all()}
        hmis_rows = {r.quarter: r for r in db.query(HMISMetric).filter(HMISMetric.village_id == village.id).all()}
        ang_rows = {r.quarter: r for r in db.query(AnganwadiMetric).filter(AnganwadiMetric.village_id == village.id).all()}
        quarters = sorted(set(rhs_rows) & set(hmis_rows) & set(ang_rows))
        if not quarters:
            continue

        ahs = district_ahs.get(village.district_id)
        district_u5mr = ahs.under5_mortality_rate if ahs else 50.0

        history = []
        for q in quarters:
            rhs, hmis, ang = rhs_rows[q], hmis_rows[q], ang_rows[q]
            gi_input = GapIndexInput(
                population=village.population,
                sub_centres_count=rhs.sub_centres_count, phc_count=rhs.phc_count,
                monthly_capacity_total=rhs.monthly_capacity_total, mmu_count=rhs.mmu_count,
                doctors_sanctioned=rhs.doctors_sanctioned, doctors_in_position=rhs.doctors_in_position,
                nurses_sanctioned=rhs.nurses_sanctioned, nurses_in_position=rhs.nurses_in_position,
                anms_in_position=rhs.anms_in_position, ashas_linked=rhs.ashas_linked,
                institutional_delivery_pct=hmis.institutional_delivery_pct,
                full_immunization_pct=hmis.full_immunization_pct,
                immunization_sessions_held=hmis.immunization_sessions_held,
                opd_utilization_pct=hmis.opd_utilization_pct,
                district_under5_mortality_rate=district_u5mr,
                severely_underweight_pct=ang.severely_underweight_pct,
                moderately_underweight_pct=ang.moderately_underweight_pct,
                growth_monitoring_pct=ang.growth_monitoring_pct,
                supplementary_nutrition_days=ang.supplementary_nutrition_days,
                distance_to_facility_km=village.distance_to_facility_km,
                has_all_weather_road=village.has_all_weather_road,
            )
            scores = compute_gap_index(gi_input)
            paradox = detect_paradox(scores)

            db.add(GapScore(
                village_id=village.id, quarter=q,
                infrastructure_score=scores.infrastructure_score, workforce_score=scores.workforce_score,
                service_score=scores.service_score, utilization_score=scores.utilization_score,
                outcome_score=scores.outcome_score, nutrition_score=scores.nutrition_score,
                accessibility_score=scores.accessibility_score, overall_gap_score=scores.overall_gap_score,
                risk_category=scores.risk_category, is_paradox=paradox.is_paradox, paradox_note=paradox.note,
            ))
            history.append({"quarter": q, **scores.as_dict()})

        village_histories[village.id] = history

    db.commit()
    logger.info("Computed Gap Index for %d villages", len(village_histories))

    # --- ML risk prediction (Module 2) ---
    trained = train_risk_model(village_histories)
    logger.info("Risk model trained: %s", "yes" if trained else "insufficient pooled data")

    priority_inputs = []
    village_by_id = {v.id: v for v in villages}

    for village_id, history in village_histories.items():
        village = village_by_id[village_id]
        pred = predict_next_quarter(trained, history)
        factors = explain_prediction(trained, pred.feature_vector)

        risk_pred = RiskPrediction(
            village_id=village_id, quarter=history[-1]["quarter"],
            current_risk=pred.current_risk, predicted_risk=pred.predicted_risk,
            risk_category=pred.risk_category, confidence=pred.confidence,
            trend_direction=pred.trend_direction, insufficient_data=pred.insufficient_data,
        )
        db.add(risk_pred)
        db.flush()  # get risk_pred.id

        for f in factors:
            db.add(RiskFactor(prediction_id=risk_pred.id, factor_name=f.factor_name,
                               contribution_pct=f.contribution_pct, direction=f.direction))

        priority_inputs.append(PriorityInput(
            village_id=village_id, predicted_risk=pred.predicted_risk,
            overall_gap_score=history[-1]["overall_gap_score"], population=village.population,
            trend_delta=pred.predicted_risk - pred.current_risk,
        ))

    db.commit()

    # --- Prioritization (Module 4) ---
    priorities = compute_priorities(priority_inputs)
    for p in priorities:
        db.add(PriorityScore(
            village_id=p.village_id, quarter=village_histories[p.village_id][-1]["quarter"],
            priority_score=p.priority_score, priority_tier=p.priority_tier,
            population_affected=p.population_affected, rank=p.rank,
        ))
    db.commit()

    # --- Intervention recommendations (Module 5 & 6) ---
    facility_by_village = {}
    for f in db.query(Facility).all():
        facility_by_village.setdefault(f.village_id, f)

    latest_gap_by_village = {
        gs.village_id: gs for gs in db.query(GapScore).all()
        if gs.quarter == village_histories.get(gs.village_id, [{}])[-1].get("quarter")
    }

    intervention_count = 0
    for village_id, history in village_histories.items():
        village = village_by_id[village_id]
        facility = facility_by_village.get(village_id)
        latest_quarter = history[-1]["quarter"]
        hmis_latest = db.query(HMISMetric).filter(
            HMISMetric.village_id == village_id, HMISMetric.quarter == latest_quarter
        ).first()
        scores = latest_gap_by_village.get(village_id)
        if scores is None:
            continue

        ctx = InterventionContext(
            population=village.population,
            has_medicine_stock=facility.has_medicine_stock if facility else 1,
            opd_utilization_pct=hmis_latest.opd_utilization_pct if hmis_latest else 50.0,
        )
        candidates = generate_interventions(scores, ctx)
        for rank, c in enumerate(candidates, start=1):
            db.add(InterventionOption(
                village_id=village_id, quarter=latest_quarter, problem_tag=c.problem_tag,
                intervention_name=c.intervention_name, category=c.category, cost_level=c.cost_level,
                cost_estimate_inr=c.cost_estimate_inr, time_months=c.time_months,
                expected_impact_score=c.expected_impact_score, impact_per_resource=c.impact_per_resource,
                coverage_population=c.coverage_population,
                is_infrastructure_expansion=c.is_infrastructure_expansion, rank=rank,
            ))
            intervention_count += 1

    db.commit()
    logger.info("Generated %d intervention options", intervention_count)

    return {
        "villages_processed": len(village_histories),
        "model_trained": trained is not None,
        "interventions_generated": intervention_count,
    }
