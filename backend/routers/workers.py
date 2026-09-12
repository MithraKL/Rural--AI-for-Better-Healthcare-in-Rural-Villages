from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.database import get_db
from backend.models import HealthWorker
from backend.schemas import HealthWorkerCreate, HealthWorkerUpdate, HealthWorkerResponse

router = APIRouter()


@router.post("/", response_model=HealthWorkerResponse, status_code=status.HTTP_201_CREATED)
def create_health_worker(worker: HealthWorkerCreate, db: Session = Depends(get_db)):
    """Create a new health worker"""
    db_worker = HealthWorker(**worker.model_dump())
    db.add(db_worker)
    db.commit()
    db.refresh(db_worker)
    return db_worker


@router.get("/", response_model=List[HealthWorkerResponse])
def get_health_workers(
    skip: int = 0,
    limit: int = 100,
    village_id: int = None,
    role: str = None,
    db: Session = Depends(get_db)
):
    """Get all health workers with optional filters"""
    query = db.query(HealthWorker)
    
    if village_id:
        query = query.filter(HealthWorker.village_id == village_id)
    if role:
        query = query.filter(HealthWorker.role == role)
    
    workers = query.offset(skip).limit(limit).all()
    return workers


@router.get("/{worker_id}", response_model=HealthWorkerResponse)
def get_health_worker(worker_id: int, db: Session = Depends(get_db)):
    """Get a specific health worker by ID"""
    worker = db.query(HealthWorker).filter(HealthWorker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Health worker not found")
    return worker


@router.put("/{worker_id}", response_model=HealthWorkerResponse)
def update_health_worker(
    worker_id: int,
    worker_update: HealthWorkerUpdate,
    db: Session = Depends(get_db)
):
    """Update a health worker"""
    db_worker = db.query(HealthWorker).filter(HealthWorker.id == worker_id).first()
    if not db_worker:
        raise HTTPException(status_code=404, detail="Health worker not found")
    
    update_data = worker_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_worker, field, value)
    
    db_worker.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_worker)
    return db_worker


@router.delete("/{worker_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_health_worker(worker_id: int, db: Session = Depends(get_db)):
    """Delete a health worker"""
    db_worker = db.query(HealthWorker).filter(HealthWorker.id == worker_id).first()
    if not db_worker:
        raise HTTPException(status_code=404, detail="Health worker not found")
    
    db.delete(db_worker)
    db.commit()
    return None
