from fastapi import APIRouter
from backend.services.gap_index import load_weights
from backend.services.paradox_detector import INFRA_HIGH_THRESHOLD, WEAK_DIMENSION_THRESHOLD
from backend.services.intervention_engine import INFRA_GAP_THRESHOLD, PROBLEM_THRESHOLD
from backend.services.resource_mismatch import OVERLOAD_UTILIZATION_PCT, UNDERUTILIZED_UTILIZATION_PCT

router = APIRouter()


@router.get("/")
def get_methodology():
    return {
        "gap_index": {
            "description": "Each of 7 dimensions is normalized to a 0-100 scale from raw source "
                            "indicators, then combined into an overall gap/risk score using configurable "
                            "weights. Higher overall score = higher risk / bigger gap.",
            "weights": load_weights(),
            "risk_categories": {"CRITICAL": ">=58", "HIGH": ">=46", "MODERATE": ">=32", "LOW": "<32"},
        },
        "paradox_detection": {
            "description": "Flags a village when Infrastructure Score is high but at least two of "
                            "Service Delivery / Utilization / Outcomes / Nutrition are low. Framed as an "
                            "associated pattern requiring field validation, never a proven cause.",
            "infrastructure_high_threshold": INFRA_HIGH_THRESHOLD,
            "weak_dimension_threshold": WEAK_DIMENSION_THRESHOLD,
        },
        "risk_prediction": {
            "description": "A RandomForestRegressor is trained on pooled quarter-over-quarter "
                            "transitions across all villages (7 gap dimensions + recent trend slope as "
                            "features) to predict next-quarter overall gap/risk score. Confidence is "
                            "derived from the dispersion of predictions across the forest's individual "
                            "trees. Villages with fewer than 3 quarters of history return "
                            "'insufficient historical data' rather than a fabricated prediction.",
            "model": "RandomForestRegressor (scikit-learn)",
        },
        "explainability": {
            "description": "Per-village driver contributions combine the model's global feature "
                            "importances with each village's deviation from the population mean for that "
                            "feature, normalized to percentages. This is a transparent, interpretable-ML "
                            "technique, not a black box.",
        },
        "prioritization": {
            "description": "Priority Score = 45% predicted risk + 25% population affected + 15% "
                            "severity (overall gap score) + 15% worsening trend.",
        },
        "intervention_engine": {
            "description": "Detected problems (low immunization, high malnutrition, low utilization, "
                            "medicine shortage, accessibility gap, facility overload, workforce gap) are "
                            "mapped to a catalogue of concrete interventions with cost/time/impact "
                            "estimates. Infrastructure expansion is only generated when the Infrastructure "
                            "dimension itself is genuinely poor (score < %s) — never as a first response.",
            "infra_gap_threshold": INFRA_GAP_THRESHOLD, "problem_threshold": PROBLEM_THRESHOLD,
        },
        "resource_optimization": {
            "description": "A greedy heuristic (not an exact LP solver) sorts candidate "
                            "village+intervention pairs by priority_score x impact_per_resource and "
                            "allocates the admin-defined resource pool until exhausted.",
        },
        "simulation": {
            "description": "What-If effects combine selected interventions' catalog impact scores with "
                            "diminishing returns (1 - product(1 - effect_i)), scaled by a funding/dosage "
                            "multiplier derived from the allocated budget and resources relative to the "
                            "interventions' estimated requirement. All outputs are projections, not "
                            "guarantees.",
        },
        "resource_mismatch": {
            "overload_utilization_pct": OVERLOAD_UTILIZATION_PCT,
            "underutilized_utilization_pct": UNDERUTILIZED_UTILIZATION_PCT,
        },
        "data_sources": {
            "RHS": "village-level (aggregated)", "HMIS": "village-level (aggregated)",
            "Anganwadi": "village-level", "NFHS": "district-level", "DLHS": "district-level",
            "AHS": "district-level",
            "note": "District-level indicators are never fabricated down to village level; the Outcome "
                    "Score is an explicitly-labeled modeled proxy blending village HMIS with district "
                    "NFHS/AHS survey data.",
        },
    }
