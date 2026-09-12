from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.models import Village, District, Block, State, GapScore, PriorityScore, Facility
from backend.schemas import VillageSummary, VillageDetail, GapScoreOut, FacilityOut

router = APIRouter()


def _latest_gap_score(db: Session, village_id: int) -> Optional[GapScore]:
    return (
        db.query(GapScore)
        .filter(GapScore.village_id == village_id)
        .order_by(GapScore.quarter.desc())
        .first()
    )


def _latest_priority(db: Session, village_id: int) -> Optional[PriorityScore]:
    return (
        db.query(PriorityScore)
        .filter(PriorityScore.village_id == village_id)
        .order_by(PriorityScore.quarter.desc())
        .first()
    )


def _to_summary(db: Session, v: Village) -> VillageSummary:
    gap = _latest_gap_score(db, v.id)
    priority = _latest_priority(db, v.id)
    return VillageSummary(
        id=v.id, name=v.name, district_name=v.district.name, block_name=v.block.name,
        state_name=v.state.name, population=v.population, latitude=v.latitude, longitude=v.longitude,
        is_demo=bool(v.is_demo),
        overall_gap_score=gap.overall_gap_score if gap else None,
        risk_category=gap.risk_category if gap else None,
        is_paradox=gap.is_paradox if gap else None,
        priority_tier=priority.priority_tier if priority else None,
    )


@router.get("/", response_model=list[VillageSummary])
def list_villages(
    district_id: Optional[int] = None,
    risk_category: Optional[str] = None,
    paradox_only: bool = False,
    search: Optional[str] = None,
    limit: int = Query(200, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(Village)
    if district_id:
        query = query.filter(Village.district_id == district_id)
    if search:
        query = query.filter(Village.name.ilike(f"%{search}%"))
    villages = query.all()

    summaries = [_to_summary(db, v) for v in villages]
    if risk_category:
        summaries = [s for s in summaries if s.risk_category == risk_category.upper()]
    if paradox_only:
        summaries = [s for s in summaries if s.is_paradox]
    return summaries[:limit]


@router.get("/{village_id}", response_model=VillageDetail)
def get_village(village_id: int, db: Session = Depends(get_db)):
    v = db.query(Village).filter(Village.id == village_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Village not found")

    summary = _to_summary(db, v)
    trend_rows = (
        db.query(GapScore).filter(GapScore.village_id == village_id).order_by(GapScore.quarter.asc()).all()
    )
    trend = [GapScoreOut.model_validate(r) for r in trend_rows]
    latest_gap = trend[-1] if trend else None

    facilities = db.query(Facility).filter(Facility.village_id == village_id).all()
    facility_out = [FacilityOut.model_validate(f) for f in facilities]

    return VillageDetail(
        **summary.model_dump(),
        gap_breakdown=latest_gap,
        trend=trend,
        facilities=facility_out,
    )
