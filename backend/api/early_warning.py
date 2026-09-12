from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.models import Village, AnganwadiMetric, HMISMetric, GapScore
from backend.schemas import EarlyWarningOut
from backend.services.early_warning import analyze_trend

router = APIRouter()

INDICATORS = {
    "malnutrition": {
        "label": "Malnutrition (severely + moderately underweight children)",
        "higher_is_worse": True, "threshold": 55.0,
    },
    "immunization": {
        "label": "Full immunization coverage",
        "higher_is_worse": False, "threshold": 40.0,
    },
    "overall_risk": {
        "label": "Overall healthcare gap/risk score",
        "higher_is_worse": True, "threshold": 75.0,
    },
}


def _series_for(db: Session, village_id: int, indicator: str):
    if indicator == "malnutrition":
        rows = (
            db.query(AnganwadiMetric)
            .filter(AnganwadiMetric.village_id == village_id)
            .order_by(AnganwadiMetric.quarter.asc())
            .all()
        )
        return [r.quarter for r in rows], [r.severely_underweight_pct + r.moderately_underweight_pct for r in rows]
    if indicator == "immunization":
        rows = (
            db.query(HMISMetric)
            .filter(HMISMetric.village_id == village_id)
            .order_by(HMISMetric.quarter.asc())
            .all()
        )
        return [r.quarter for r in rows], [r.full_immunization_pct for r in rows]
    rows = (
        db.query(GapScore)
        .filter(GapScore.village_id == village_id)
        .order_by(GapScore.quarter.asc())
        .all()
    )
    return [r.quarter for r in rows], [r.overall_gap_score for r in rows]


@router.get("/", response_model=list[EarlyWarningOut])
def early_warnings(
    indicator: str = Query("malnutrition", pattern="^(malnutrition|immunization|overall_risk)$"),
    district_id: Optional[int] = None,
    worsening_only: bool = True,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    cfg = INDICATORS[indicator]
    query = db.query(Village)
    if district_id:
        query = query.filter(Village.district_id == district_id)
    villages = query.all()

    results = []
    for v in villages:
        quarters, values = _series_for(db, v.id, indicator)
        if not values:
            continue
        warning = analyze_trend(values, cfg["label"], higher_is_worse=cfg["higher_is_worse"], threshold=cfg["threshold"])
        if worsening_only and warning.direction != "worsening":
            continue
        results.append(EarlyWarningOut(
            village_id=v.id, village_name=v.name, indicator=indicator,
            trend_values=values, quarters=quarters, direction=warning.direction,
            message=warning.message, periods_to_threshold=warning.periods_to_threshold,
        ))

    results.sort(key=lambda r: (r.periods_to_threshold is None, r.periods_to_threshold or 0))
    return results[:limit]
