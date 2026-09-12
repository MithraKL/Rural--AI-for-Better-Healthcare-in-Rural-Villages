from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.models import Facility, HMISMetric, Village
from backend.schemas import FacilityOut, FacilityMismatchOut
from backend.services.resource_mismatch import FacilityLoadInput, detect_mismatch

router = APIRouter()


@router.get("/", response_model=list[FacilityOut])
def list_facilities(district_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Facility)
    if district_id:
        query = query.filter(Facility.district_id == district_id)
    return query.all()


@router.get("/mismatch", response_model=list[FacilityMismatchOut])
def facility_mismatch(district_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Module 9 — Resource Wastage / Mismatch Detection."""
    query = db.query(Facility)
    if district_id:
        query = query.filter(Facility.district_id == district_id)
    facilities = query.all()

    results = []
    for f in facilities:
        latest_hmis = (
            db.query(HMISMetric)
            .filter(HMISMetric.village_id == f.village_id)
            .order_by(HMISMetric.quarter.desc())
            .first()
        )
        village = db.query(Village).filter(Village.id == f.village_id).first() if f.village_id else None
        mismatch = detect_mismatch(FacilityLoadInput(
            facility_id=f.id, facility_name=f.name, facility_type=f.facility_type,
            village_name=village.name if village else None,
            doctors_sanctioned=f.doctors_sanctioned, doctors_in_position=f.doctors_in_position,
            utilization_pct=latest_hmis.opd_utilization_pct if latest_hmis else None,
        ))
        results.append(FacilityMismatchOut(**mismatch.__dict__))

    priority_order = {"OVERLOADED": 0, "UNDER_RESOURCED": 1, "UNDERUTILIZED": 2, "BALANCED": 3}
    results.sort(key=lambda r: priority_order.get(r.mismatch_type, 9))
    return results
