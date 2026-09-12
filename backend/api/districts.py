from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import District
from backend.schemas import DistrictOut

router = APIRouter()


@router.get("/", response_model=list[DistrictOut])
def list_districts(db: Session = Depends(get_db)):
    districts = db.query(District).all()
    return [DistrictOut(id=d.id, name=d.name, state_name=d.state.name, population=d.population) for d in districts]
