from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.database import get_db
from backend.models import HealthRecord
from backend.schemas import HealthRecordCreate, HealthRecordUpdate, HealthRecordResponse

router = APIRouter()


@router.post("/", response_model=HealthRecordResponse, status_code=status.HTTP_201_CREATED)
def create_health_record(record: HealthRecordCreate, db: Session = Depends(get_db)):
    """Create a new health record"""
    db_record = HealthRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.get("/", response_model=List[HealthRecordResponse])
def get_health_records(
    skip: int = 0,
    limit: int = 100,
    village_id: int = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Get all health records with optional filters"""
    query = db.query(HealthRecord)
    
    if village_id:
        query = query.filter(HealthRecord.village_id == village_id)
    if status:
        query = query.filter(HealthRecord.status == status)
    
    records = query.offset(skip).limit(limit).all()
    return records


@router.get("/{record_id}", response_model=HealthRecordResponse)
def get_health_record(record_id: int, db: Session = Depends(get_db)):
    """Get a specific health record by ID"""
    record = db.query(HealthRecord).filter(HealthRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Health record not found")
    return record


@router.put("/{record_id}", response_model=HealthRecordResponse)
def update_health_record(
    record_id: int,
    record_update: HealthRecordUpdate,
    db: Session = Depends(get_db)
):
    """Update a health record"""
    db_record = db.query(HealthRecord).filter(HealthRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Health record not found")
    
    update_data = record_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_record, field, value)
    
    db_record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_record)
    return db_record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_health_record(record_id: int, db: Session = Depends(get_db)):
    """Delete a health record"""
    db_record = db.query(HealthRecord).filter(HealthRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Health record not found")
    
    db.delete(db_record)
    db.commit()
    return None
