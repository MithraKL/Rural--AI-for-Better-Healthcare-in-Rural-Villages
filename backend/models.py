from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class Village(Base):
    """Village model for managing rural areas"""
    __tablename__ = "villages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    population = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    health_records = relationship("HealthRecord", back_populates="village", cascade="all, delete-orphan")
    workers = relationship("HealthWorker", back_populates="village", cascade="all, delete-orphan")


class HealthWorker(Base):
    """Health worker model for frontline staff"""
    __tablename__ = "health_workers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)  # Anganwadi, ASHA, ANM, etc.
    phone = Column(String(15), nullable=False)
    email = Column(String(100), nullable=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    village = relationship("Village", back_populates="workers")
    health_records = relationship("HealthRecord", back_populates="recorded_by_worker")


class HealthRecord(Base):
    """Health record model for patient data"""
    __tablename__ = "health_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String(100), nullable=False)
    patient_age = Column(Integer, nullable=False)
    patient_gender = Column(String(10), nullable=False)
    patient_phone = Column(String(15), nullable=True)
    
    # Health metrics
    condition = Column(String(200), nullable=False)
    symptoms = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    treatment = Column(Text, nullable=True)
    
    # Status tracking
    status = Column(String(50), default="active")  # active, resolved, referred
    priority = Column(String(20), default="normal")  # low, normal, high, critical
    
    # References
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("health_workers.id"), nullable=False)
    
    # Timestamps
    visit_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    village = relationship("Village", back_populates="health_records")
    recorded_by_worker = relationship("HealthWorker", back_populates="health_records")
