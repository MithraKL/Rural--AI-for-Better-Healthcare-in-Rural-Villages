from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import RiskPrediction, Village, GapScore
from backend.schemas import ExplanationOut, RiskFactorOut
from backend.services.genai_explainer import ExplanationInput, generate_explanation

router = APIRouter()


@router.get("/{village_id}", response_model=ExplanationOut)
def get_explanation(village_id: int, db: Session = Depends(get_db)):
    village = db.query(Village).filter(Village.id == village_id).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    pred = (
        db.query(RiskPrediction)
        .filter(RiskPrediction.village_id == village_id)
        .order_by(RiskPrediction.quarter.desc())
        .first()
    )
    if not pred:
        raise HTTPException(status_code=404, detail="Insufficient data to generate an explanation for this village.")

    gap = (
        db.query(GapScore)
        .filter(GapScore.village_id == village_id)
        .order_by(GapScore.quarter.desc())
        .first()
    )

    # Only factors that *increase* risk belong in the "why is this high risk" narrative;
    # protective factors (e.g. adequate infrastructure) are shown separately in `drivers`.
    risk_increasing = [f for f in pred.factors if f.direction == "increases"]
    top_factors = [(f.factor_name, f.contribution_pct) for f in
                   sorted(risk_increasing, key=lambda f: f.contribution_pct, reverse=True)]

    result = generate_explanation(ExplanationInput(
        village_name=village.name, predicted_risk=pred.predicted_risk, risk_category=pred.risk_category,
        is_paradox=bool(gap.is_paradox) if gap else False, paradox_note=gap.paradox_note if gap else None,
        top_factors=top_factors,
    ))

    return ExplanationOut(
        village_id=village_id, village_name=village.name, headline=result.headline,
        narrative=result.narrative,
        drivers=[RiskFactorOut(factor_name=f.factor_name, contribution_pct=f.contribution_pct, direction=f.direction)
                 for f in pred.factors],
        is_paradox=bool(gap.is_paradox) if gap else False, generated_by=result.generated_by,
    )
