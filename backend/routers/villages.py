from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.database import get_db
from backend.models import Village
from backend.schemas import VillageCreate, VillageUpdate, VillageResponse

router = APIRouter()


@router.post("/", response_model=VillageResponse, status_code=status.HTTP_201_CREATED)
def create_village(village: VillageCreate, db: Session = Depends(get_db)):
    """Create a new village"""
    db_village = Village(**village.model_dump())
    db.add(db_village)
    db.commit()
    db.refresh(db_village)
    return db_village


@router.get("/", response_model=List[VillageResponse])
def get_villages(
    skip: int = 0,
    limit: int = 100,
    district: str = None,
    db: Session = Depends(get_db)
):
    """Get all villages with optional filters"""
    query = db.query(Village)
    
    if district:
        query = query.filter(Village.district == district)
    
    villages = query.offset(skip).limit(limit).all()
    return villages


@router.get("/{village_id}", response_model=VillageResponse)
def get_village(village_id: int, db: Session = Depends(get_db)):
    """Get a specific village by ID"""
    village = db.query(Village).filter(Village.id == village_id).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    return village


@router.put("/{village_id}", response_model=VillageResponse)
def update_village(
    village_id: int,
    village_update: VillageUpdate,
    db: Session = Depends(get_db)
):
    """Update a village"""
    db_village = db.query(Village).filter(Village.id == village_id).first()
    if not db_village:
        raise HTTPException(status_code=404, detail="Village not found")
    
    update_data = village_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_village, field, value)
    
    db_village.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_village)
    return db_village


@router.delete("/{village_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_village(village_id: int, db: Session = Depends(get_db)):
    """Delete a village"""
    db_village = db.query(Village).filter(Village.id == village_id).first()
    if not db_village:
        raise HTTPException(status_code=404, detail="Village not found")
    
    db.delete(db_village)
    db.commit()
    return None
