"""Import every model module so Base.metadata.create_all() sees all tables."""
from backend.models.geography import State, District, Block, Village
from backend.models.facility import Facility, FACILITY_TYPES
from backend.models.metrics import (
    RHSMetric, HMISMetric, NFHSMetric, DLHSMetric, AHSMetric, AnganwadiMetric,
)
from backend.models.intelligence import (
    GapScore, RiskPrediction, RiskFactor, PriorityScore, InterventionOption,
    ResourcePool, ResourceAllocation, SimulationResult, DatasetMetadata,
)

__all__ = [
    "State", "District", "Block", "Village",
    "Facility", "FACILITY_TYPES",
    "RHSMetric", "HMISMetric", "NFHSMetric", "DLHSMetric", "AHSMetric", "AnganwadiMetric",
    "GapScore", "RiskPrediction", "RiskFactor", "PriorityScore", "InterventionOption",
    "ResourcePool", "ResourceAllocation", "SimulationResult", "DatasetMetadata",
]
