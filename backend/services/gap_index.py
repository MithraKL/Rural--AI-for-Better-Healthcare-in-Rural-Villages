"""Module 1 — Healthcare Gap Detector.

Computes a multi-dimensional Healthcare Gap Index for a village at a given
quarter. Every raw source indicator is first normalized onto a comparable
0-100 scale (never raw-averaged), then combined into an overall gap/risk
score using configurable weights (see weights.json).

Dimensions: Infrastructure, Workforce, Service Delivery, Utilization,
Outcomes, Nutrition, Accessibility.
"""
import json
import os
from dataclasses import dataclass, asdict

_WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "weights.json")


def load_weights() -> dict:
    with open(_WEIGHTS_PATH, "r") as f:
        raw = json.load(f)
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def _clip(v, lo=0.0, hi=100.0):
    return max(lo, min(hi, v))


def _clip01(v):
    return max(0.0, min(1.0, v))


@dataclass
class GapIndexInput:
    population: int

    # infrastructure
    sub_centres_count: int
    phc_count: int
    monthly_capacity_total: int
    mmu_count: int

    # workforce
    doctors_sanctioned: int
    doctors_in_position: int
    nurses_sanctioned: int
    nurses_in_position: int
    anms_in_position: int
    ashas_linked: int

    # service delivery
    institutional_delivery_pct: float
    full_immunization_pct: float
    immunization_sessions_held: int

    # utilization
    opd_utilization_pct: float

    # outcomes (blends village HMIS with district-level NFHS/AHS survey data —
    # this is a *derived modeled proxy*, not a village-level NFHS reading)
    district_under5_mortality_rate: float

    # nutrition (Anganwadi)
    severely_underweight_pct: float
    moderately_underweight_pct: float
    growth_monitoring_pct: float
    supplementary_nutrition_days: int

    # accessibility
    distance_to_facility_km: float
    has_all_weather_road: int


@dataclass
class GapIndexResult:
    infrastructure_score: float
    workforce_score: float
    service_score: float
    utilization_score: float
    outcome_score: float
    nutrition_score: float
    accessibility_score: float
    overall_gap_score: float
    risk_category: str

    def as_dict(self):
        return asdict(self)


def _risk_category(overall_gap_score: float) -> str:
    if overall_gap_score >= 58:
        return "CRITICAL"
    if overall_gap_score >= 46:
        return "HIGH"
    if overall_gap_score >= 32:
        return "MODERATE"
    return "LOW"


def compute_gap_index(x: GapIndexInput, weights: dict | None = None) -> GapIndexResult:
    weights = weights or load_weights()
    pop = max(x.population, 1)

    # --- Infrastructure ---
    expected_sc = pop / 5000.0
    expected_phc = pop / 30000.0
    facility_ratio = _clip01(
        0.5 * (x.sub_centres_count / max(expected_sc, 0.2))
        + 0.5 * (x.phc_count / max(expected_phc, 0.2))
    )
    capacity_ratio = _clip01(x.monthly_capacity_total / (pop * 0.03))
    mmu_bonus = 1.0 if x.mmu_count > 0 else 0.0
    infrastructure_score = 100 * _clip01(0.55 * facility_ratio + 0.35 * capacity_ratio + 0.10 * mmu_bonus)

    # --- Workforce ---
    doctor_fill = min(x.doctors_in_position / max(x.doctors_sanctioned, 1), 1.0)
    nurse_fill = min(x.nurses_in_position / max(x.nurses_sanctioned, 1), 1.0)
    anm_ratio = _clip01(x.anms_in_position / max(pop / 3000.0, 0.5))
    asha_ratio = _clip01(x.ashas_linked / max(pop / 1000.0, 0.5))
    workforce_score = 100 * _clip01(0.35 * doctor_fill + 0.25 * nurse_fill + 0.20 * anm_ratio + 0.20 * asha_ratio)

    # --- Service Delivery ---
    service_score = 100 * _clip01(
        0.4 * (x.institutional_delivery_pct / 100)
        + 0.4 * (x.full_immunization_pct / 100)
        + 0.2 * _clip01(x.immunization_sessions_held / 4.0)
    )

    # --- Utilization --- (80% OPD utilization treated as the "fully used" target; overload is flagged separately)
    utilization_score = 100 * _clip01(x.opd_utilization_pct / 75.0)

    # --- Outcomes (modeled proxy) ---
    outcome_score = 100 * _clip01(
        0.5 * (x.full_immunization_pct / 100)
        + 0.3 * (1 - _clip01(x.district_under5_mortality_rate / 100))
        + 0.2 * (x.institutional_delivery_pct / 100)
    )

    # --- Nutrition ---
    malnutrition_composite = x.severely_underweight_pct * 1.5 + x.moderately_underweight_pct * 0.5
    nutrition_score = 100 * _clip01(
        0.6 * (1 - _clip01(malnutrition_composite / 60.0))
        + 0.25 * (x.growth_monitoring_pct / 100)
        + 0.15 * _clip01(x.supplementary_nutrition_days / 90.0)
    )

    # --- Accessibility ---
    distance_component = _clip01(1 - x.distance_to_facility_km / 15.0)
    accessibility_score = 100 * _clip01(0.7 * distance_component + 0.3 * x.has_all_weather_road)

    scores = {
        "infrastructure": infrastructure_score,
        "workforce": workforce_score,
        "service": service_score,
        "utilization": utilization_score,
        "outcome": outcome_score,
        "nutrition": nutrition_score,
        "accessibility": accessibility_score,
    }
    # Weighted-average gap, blended with the single worst-performing dimension's
    # gap ("weakest link"). A village can be pulled into HIGH/CRITICAL risk by one
    # severely failing dimension even if most others are adequate — matching the
    # real-world pattern where a single acute gap (e.g. a nutrition crisis) drives
    # risk regardless of a healthy average.
    gaps = {k: 100 - v for k, v in scores.items()}
    weighted_gap = sum(gaps[k] * weights.get(k, 0) for k in gaps)
    worst_gap = max(gaps.values())
    overall_gap_score = _clip(0.65 * weighted_gap + 0.35 * worst_gap, 0, 100)

    return GapIndexResult(
        infrastructure_score=round(infrastructure_score, 1),
        workforce_score=round(workforce_score, 1),
        service_score=round(service_score, 1),
        utilization_score=round(utilization_score, 1),
        outcome_score=round(outcome_score, 1),
        nutrition_score=round(nutrition_score, 1),
        accessibility_score=round(accessibility_score, 1),
        overall_gap_score=round(overall_gap_score, 1),
        risk_category=_risk_category(overall_gap_score),
    )
