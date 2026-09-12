from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import GapScore, Village, Facility, HMISMetric, InterventionOption
from backend.schemas import DashboardKPIs
from backend.config import settings

router = APIRouter()


@router.get("/kpis", response_model=DashboardKPIs)
def dashboard_kpis(db: Session = Depends(get_db)):
    total_villages = db.query(Village).count()

    latest_by_village = {}
    for gs in db.query(GapScore).order_by(GapScore.quarter.asc()).all():
        latest_by_village[gs.village_id] = gs

    critical = sum(1 for gs in latest_by_village.values() if gs.risk_category == "CRITICAL")
    emerging = sum(1 for gs in latest_by_village.values() if gs.risk_category == "HIGH")

    villages_by_id = {v.id: v for v in db.query(Village).all()}
    at_risk_population = sum(
        villages_by_id[vid].population for vid, gs in latest_by_village.items()
        if gs.risk_category in ("CRITICAL", "HIGH") and vid in villages_by_id
    )

    facilities = db.query(Facility).all()
    high_risk_facilities = sum(1 for f in facilities if f.doctors_in_position < f.doctors_sanctioned * 0.5)

    hmis_latest = {}
    for h in db.query(HMISMetric).order_by(HMISMetric.quarter.asc()).all():
        hmis_latest[h.village_id] = h
    if hmis_latest:
        resource_utilization_pct = round(
            sum(min(h.opd_utilization_pct, 100) for h in hmis_latest.values()) / len(hmis_latest), 1
        )
    else:
        resource_utilization_pct = 0.0

    top_interventions = (
        db.query(InterventionOption).order_by(InterventionOption.expected_impact_score.desc()).limit(20).all()
    )
    potential_impact_score = round(
        sum(i.expected_impact_score for i in top_interventions) / len(top_interventions), 1
    ) if top_interventions else 0.0

    latest_quarter = max((gs.quarter for gs in latest_by_village.values()), default="")

    return DashboardKPIs(
        critical_villages=critical, emerging_risk_villages=emerging,
        at_risk_population=at_risk_population, high_risk_facilities=high_risk_facilities,
        total_villages=total_villages, resource_utilization_pct=resource_utilization_pct,
        potential_impact_score=potential_impact_score, is_demo_data=settings.DEMO_MODE,
        quarter=latest_quarter,
    )
