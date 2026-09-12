from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Village Schemas
class VillageBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    district: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    population: int = Field(..., gt=0)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class VillageCreate(VillageBase):
    pass


class VillageUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    district: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    population: Optional[int] = Field(None, gt=0)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class VillageResponse(VillageBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Health Worker Schemas
class HealthWorkerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=10, max_length=15)
    email: Optional[str] = Field(None, max_length=100)
    village_id: int = Field(..., gt=0)
    is_active: bool = True


class HealthWorkerCreate(HealthWorkerBase):
    pass


class HealthWorkerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    email: Optional[str] = Field(None, max_length=100)
    village_id: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None


class HealthWorkerResponse(HealthWorkerBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Health Record Schemas
class HealthRecordBase(BaseModel):
    patient_name: str = Field(..., min_length=1, max_length=100)
    patient_age: int = Field(..., ge=0, le=150)
    patient_gender: str = Field(..., min_length=1, max_length=10)
    patient_phone: Optional[str] = Field(None, max_length=15)
    condition: str = Field(..., min_length=1, max_length=200)
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    status: str = Field(default="active", max_length=50)
    priority: str = Field(default="normal", max_length=20)
    village_id: int = Field(..., gt=0)
    worker_id: int = Field(..., gt=0)


class HealthRecordCreate(HealthRecordBase):
    pass


class HealthRecordUpdate(BaseModel):
    patient_name: Optional[str] = Field(None, min_length=1, max_length=100)
    patient_age: Optional[int] = Field(None, ge=0, le=150)
    patient_gender: Optional[str] = Field(None, min_length=1, max_length=10)
    patient_phone: Optional[str] = Field(None, max_length=15)
    condition: Optional[str] = Field(None, min_length=1, max_length=200)
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)
    priority: Optional[str] = Field(None, max_length=20)
    village_id: Optional[int] = Field(None, gt=0)
    worker_id: Optional[int] = Field(None, gt=0)


class HealthRecordResponse(HealthRecordBase):
    id: int
    visit_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
