from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import InterventionOption, Village
from backend.schemas import InterventionOptionOut

router = APIRouter()


@router.get("/{village_id}", response_model=list[InterventionOptionOut])
def get_interventions(village_id: int, db: Session = Depends(get_db)):
    village = db.query(Village).filter(Village.id == village_id).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    latest_quarter = (
        db.query(InterventionOption.quarter)
        .filter(InterventionOption.village_id == village_id)
        .order_by(InterventionOption.quarter.desc())
        .first()
    )
    if not latest_quarter:
        return []

    rows = (
        db.query(InterventionOption)
        .filter(InterventionOption.village_id == village_id, InterventionOption.quarter == latest_quarter[0])
        .order_by(InterventionOption.rank.asc())
        .all()
    )
    return rows
