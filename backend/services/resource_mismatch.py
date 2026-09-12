"""Module 9 — Resource Wastage / Mismatch Detection.

Flags facilities that appear over- or under-loaded relative to their
staffing, and facilities with adequate staff but very low patient
utilization. Output is always framed as a planning suggestion requiring
administrative validation — never an automatic staff-transfer order.
"""
from dataclasses import dataclass

OVERLOAD_UTILIZATION_PCT = 115.0
UNDERUTILIZED_UTILIZATION_PCT = 30.0
UNDER_RESOURCED_FILL_RATIO = 0.5


@dataclass
class FacilityLoadInput:
    facility_id: int
    facility_name: str
    facility_type: str
    village_name: str | None
    doctors_sanctioned: int
    doctors_in_position: int
    utilization_pct: float | None


@dataclass
class MismatchResult:
    facility_id: int
    facility_name: str
    facility_type: str
    village_name: str | None
    doctors_in_position: int
    utilization_pct: float | None
    mismatch_type: str
    note: str


def detect_mismatch(f: FacilityLoadInput) -> MismatchResult:
    fill_ratio = f.doctors_in_position / max(f.doctors_sanctioned, 1)
    util = f.utilization_pct

    if util is not None and util >= OVERLOAD_UTILIZATION_PCT:
        mismatch_type = "OVERLOADED"
        note = (
            f"Patient load is {util:.0f}% of rated capacity, against "
            f"{f.doctors_in_position} of {f.doctors_sanctioned} sanctioned doctors in position. "
            f"Potential resource imbalance — recommend a review of redistribution/outreach strategy."
        )
    elif f.doctors_in_position == 0 or fill_ratio < UNDER_RESOURCED_FILL_RATIO:
        mismatch_type = "UNDER_RESOURCED"
        note = (
            f"Only {f.doctors_in_position} of {f.doctors_sanctioned} sanctioned doctors are in position. "
            f"Potential under-resourcing — recommend administrative review of staff deployment."
        )
    elif util is not None and util <= UNDERUTILIZED_UTILIZATION_PCT and fill_ratio >= 0.8:
        mismatch_type = "UNDERUTILIZED"
        note = (
            f"Staffing appears adequate ({f.doctors_in_position} doctors in position) but utilization is "
            f"only {util:.0f}% of capacity. Potential resource mismatch — recommend reviewing outreach/awareness "
            f"strategy before reallocating staff elsewhere."
        )
    else:
        mismatch_type = "BALANCED"
        note = "Staffing and utilization appear reasonably balanced for this facility."

    return MismatchResult(
        facility_id=f.facility_id, facility_name=f.facility_name, facility_type=f.facility_type,
        village_name=f.village_name, doctors_in_position=f.doctors_in_position,
        utilization_pct=util, mismatch_type=mismatch_type, note=note,
    )
