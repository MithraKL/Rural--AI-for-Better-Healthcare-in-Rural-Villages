"""Module 3 — Explainable AI.

Produces per-prediction "WHY?" breakdowns using the trained RandomForest's
global feature importances combined with each village's deviation from the
population mean for that feature. This is a standard, transparent
interpretable-ML technique (documented on the Methodology page) — no
fabricated explanations, and it degrades gracefully to "insufficient data"
when there is no trained model.
"""
from dataclasses import dataclass
import numpy as np

FRIENDLY_LABELS = {
    "infrastructure_score": "Infrastructure adequacy",
    "workforce_score": "Workforce adequacy",
    "service_score": "Service delivery",
    "utilization_score": "Healthcare utilization",
    "outcome_score": "Health outcomes",
    "nutrition_score": "Nutrition indicators",
    "accessibility_score": "Accessibility",
    "recent_trend_slope": "Recent worsening trend",
}


@dataclass
class FactorContribution:
    factor_name: str
    contribution_pct: float
    direction: str  # "increases" | "decreases"


def explain_prediction(trained, feature_vector: list[float]) -> list[FactorContribution]:
    if trained is None or feature_vector is None:
        return []

    importances = trained.model.feature_importances_
    means = trained.feature_means
    values = np.array(feature_vector)

    raw_scores = []
    for name, importance, mean_v, value in zip(trained.feature_names, importances, means, values):
        if name == "recent_trend_slope":
            # positive slope (rising gap score) directly increases risk
            deviation = value
        else:
            # a *lower* score than average represents a gap, which increases risk
            deviation = mean_v - value
        raw_scores.append((name, importance * deviation))

    total_abs = sum(abs(s) for _, s in raw_scores) or 1.0
    contributions = []
    for name, score in raw_scores:
        pct = abs(score) / total_abs * 100
        direction = "increases" if score > 0 else "decreases"
        contributions.append(FactorContribution(
            factor_name=FRIENDLY_LABELS.get(name, name),
            contribution_pct=round(pct, 1),
            direction=direction,
        ))

    contributions.sort(key=lambda c: c.contribution_pct, reverse=True)
    return contributions
