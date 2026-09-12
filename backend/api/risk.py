from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.models import RiskPrediction, Village
from backend.schemas import RiskPredictionOut, RiskFactorOut

router = APIRouter()


@router.get("/", response_model=list[RiskPredictionOut])
def list_risk(
    risk_category: Optional[str] = None,
    district_id: Optional[int] = None,
    limit: int = Query(200, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(RiskPrediction).join(Village, Village.id == RiskPrediction.village_id)
    if district_id:
        query = query.filter(Village.district_id == district_id)
    rows = query.limit(limit).all()

    out = []
    for r in rows:
        if risk_category and r.risk_category != risk_category.upper():
            continue
        factors = [RiskFactorOut.model_validate(f) for f in r.factors]
        out.append(RiskPredictionOut(
            village_id=r.village_id, quarter=r.quarter, current_risk=r.current_risk,
            predicted_risk=r.predicted_risk, prediction_horizon=r.prediction_horizon,
            risk_category=r.risk_category, confidence=r.confidence, trend_direction=r.trend_direction,
            insufficient_data=r.insufficient_data, factors=factors,
        ))
    out.sort(key=lambda r: r.predicted_risk, reverse=True)
    return out
