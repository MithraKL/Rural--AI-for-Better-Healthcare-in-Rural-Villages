from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.models import PriorityScore, Village
from backend.schemas import PriorityOut
from backend.models import RiskPrediction

router = APIRouter()


@router.get("/", response_model=list[PriorityOut])
def list_priorities(
    district_id: Optional[int] = None,
    tier: Optional[str] = None,
    limit: int = Query(200, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(PriorityScore).join(Village, Village.id == PriorityScore.village_id)
    if district_id:
        query = query.filter(Village.district_id == district_id)
    rows = query.order_by(PriorityScore.rank.asc()).limit(limit).all()

    out = []
    for p in rows:
        if tier and p.priority_tier != tier.upper():
            continue
        village = db.query(Village).filter(Village.id == p.village_id).first()
        risk = (
            db.query(RiskPrediction)
            .filter(RiskPrediction.village_id == p.village_id)
            .order_by(RiskPrediction.quarter.desc())
            .first()
        )
        out.append(PriorityOut(
            village_id=p.village_id, village_name=village.name, district_name=village.district.name,
            priority_score=p.priority_score, priority_tier=p.priority_tier,
            risk_score=risk.predicted_risk if risk else 0.0,
            population_affected=p.population_affected, rank=p.rank,
        ))
    return out
