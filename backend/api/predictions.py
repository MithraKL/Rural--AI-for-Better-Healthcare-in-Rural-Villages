from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import RiskPrediction
from backend.schemas import RiskPredictionOut, RiskFactorOut

router = APIRouter()


@router.get("/{village_id}", response_model=RiskPredictionOut)
def get_prediction(village_id: int, db: Session = Depends(get_db)):
    r = (
        db.query(RiskPrediction)
        .filter(RiskPrediction.village_id == village_id)
        .order_by(RiskPrediction.quarter.desc())
        .first()
    )
    if not r:
        raise HTTPException(status_code=404, detail="No prediction available for this village yet.")

    return RiskPredictionOut(
        village_id=r.village_id, quarter=r.quarter, current_risk=r.current_risk,
        predicted_risk=r.predicted_risk, prediction_horizon=r.prediction_horizon,
        risk_category=r.risk_category, confidence=r.confidence, trend_direction=r.trend_direction,
        insufficient_data=r.insufficient_data,
        factors=[RiskFactorOut.model_validate(f) for f in r.factors],
    )
