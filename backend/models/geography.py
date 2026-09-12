"""Geographic Harmonization Layer.

Different data sources publish at different geographic granularities
(state / district / block / village / facility). These models let every
higher-level entity be referenced directly, so a district-only indicator
(e.g. NFHS) never needs to be faked down to village level.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)

    districts = relationship("District", back_populates="state", cascade="all, delete-orphan")


class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
    population = Column(Integer, nullable=True)

    state = relationship("State", back_populates="districts")
    blocks = relationship("Block", back_populates="district", cascade="all, delete-orphan")


class Block(Base):
    """Block / sub-district."""
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    population = Column(Integer, nullable=True)

    district = relationship("District", back_populates="blocks")
    villages = relationship("Village", back_populates="block", cascade="all, delete-orphan")


class Village(Base):
    __tablename__ = "villages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)  # denormalized for fast queries
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)  # denormalized for fast queries

    population = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Accessibility proxies (used by the Accessibility dimension of the Gap Index)
    distance_to_facility_km = Column(Float, default=0.0)
    has_all_weather_road = Column(Integer, default=1)

    # Geographic harmonization metadata: not every indicator this village shows
    # is actually measured at village granularity (some are inherited from the
    # district). This is surfaced in the UI rather than hidden.
    is_demo = Column(Integer, default=1)  # 1 = synthetic demo data, 0 = real uploaded data

    block = relationship("Block", back_populates="villages")
    district = relationship("District", foreign_keys=[district_id], viewonly=True)
    state = relationship("State", foreign_keys=[state_id], viewonly=True)
    facilities = relationship("Facility", back_populates="village", cascade="all, delete-orphan")
