from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


FACILITY_TYPES = ["Sub-Centre", "PHC", "CHC", "Hospital", "Mobile Medical Unit"]


class Facility(Base):
    """RHS: physical healthcare infrastructure (Sub-Centre / PHC / CHC / Hospital / MMU)."""
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    facility_type = Column(String(50), nullable=False)  # one of FACILITY_TYPES

    village_id = Column(Integer, ForeignKey("villages.id"), nullable=True)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Workforce (RHS)
    doctors_sanctioned = Column(Integer, default=0)
    doctors_in_position = Column(Integer, default=0)
    nurses_sanctioned = Column(Integer, default=0)
    nurses_in_position = Column(Integer, default=0)
    anms_in_position = Column(Integer, default=0)
    ashas_linked = Column(Integer, default=0)

    # Infrastructure / capacity (RHS)
    beds = Column(Integer, default=0)
    monthly_patient_capacity = Column(Integer, default=0)
    has_functional_equipment = Column(Integer, default=1)  # boolean-ish, demo simplification
    has_medicine_stock = Column(Integer, default=1)

    village = relationship("Village", back_populates="facilities")
