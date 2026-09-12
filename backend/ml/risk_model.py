"""Module 2 — Risk Prediction.

Trains a RandomForestRegressor on historical quarter-over-quarter transitions
of the Healthcare Gap Index to predict each village's risk score for the
next quarter. No LLM is used for numerical prediction anywhere in this
module — this is a genuine statistical/ML model over structured features.

Confidence is derived from the dispersion of predictions across the forest's
individual trees (a standard, honest way to express uncertainty for a
RandomForest without needing a separate probabilistic model).
"""
from dataclasses import dataclass
import numpy as np
from sklearn.ensemble import RandomForestRegressor

FEATURE_NAMES = [
    "infrastructure_score", "workforce_score", "service_score", "utilization_score",
    "outcome_score", "nutrition_score", "accessibility_score", "recent_trend_slope",
]
MIN_QUARTERS_FOR_PREDICTION = 3


def _risk_category(score: float) -> str:
    if score >= 58:
        return "CRITICAL"
    if score >= 46:
        return "HIGH"
    if score >= 32:
        return "MODERATE"
    return "LOW"


def _trend_slope(overall_scores: list[float]) -> float:
    if len(overall_scores) < 2:
        return 0.0
    x = np.arange(len(overall_scores), dtype=float)
    slope, _ = np.polyfit(x, overall_scores, 1)
    return float(slope)


def _feature_row(dims: dict, trend_slope: float) -> list[float]:
    return [
        dims["infrastructure_score"], dims["workforce_score"], dims["service_score"],
        dims["utilization_score"], dims["outcome_score"], dims["nutrition_score"],
        dims["accessibility_score"], trend_slope,
    ]


@dataclass
class TrainedRiskModel:
    model: RandomForestRegressor
    feature_means: np.ndarray
    feature_names: list


def train_risk_model(village_histories: dict[int, list[dict]]) -> TrainedRiskModel | None:
    """village_histories: {village_id: [ {quarter, infrastructure_score, ..., overall_gap_score}, ... ] }
    ordered oldest -> newest. Builds quarter(t) -> quarter(t+1) training rows pooled across villages.
    """
    X, y = [], []
    for village_id, history in village_histories.items():
        if len(history) < 2:
            continue
        overall_so_far = []
        for i in range(len(history) - 1):
            cur, nxt = history[i], history[i + 1]
            overall_so_far.append(cur["overall_gap_score"])
            slope = _trend_slope(overall_so_far) if len(overall_so_far) >= 2 else 0.0
            X.append(_feature_row(cur, slope))
            y.append(nxt["overall_gap_score"])

    if len(X) < 10:
        return None

    X = np.array(X)
    y = np.array(y)
    model = RandomForestRegressor(n_estimators=200, max_depth=6, min_samples_leaf=2, random_state=42)
    model.fit(X, y)
    return TrainedRiskModel(model=model, feature_means=X.mean(axis=0), feature_names=FEATURE_NAMES)


@dataclass
class RiskPredictionResult:
    current_risk: float
    predicted_risk: float
    risk_category: str
    confidence: float
    trend_direction: str
    insufficient_data: bool
    feature_vector: list[float] | None = None


def predict_next_quarter(trained: TrainedRiskModel | None, history: list[dict]) -> RiskPredictionResult:
    current_risk = history[-1]["overall_gap_score"] if history else 0.0

    if trained is None or len(history) < MIN_QUARTERS_FOR_PREDICTION:
        return RiskPredictionResult(
            current_risk=round(current_risk, 1), predicted_risk=round(current_risk, 1),
            risk_category=_risk_category(current_risk), confidence=0.0,
            trend_direction="stable", insufficient_data=True,
        )

    overall_series = [h["overall_gap_score"] for h in history]
    slope = _trend_slope(overall_series)
    features = np.array([_feature_row(history[-1], slope)])

    tree_preds = np.array([t.predict(features)[0] for t in trained.model.estimators_])
    predicted_risk = float(np.clip(tree_preds.mean(), 0, 100))
    std = float(tree_preds.std())
    confidence = float(np.clip(1 - std / 25.0, 0.35, 0.97))

    delta = predicted_risk - current_risk
    trend_direction = "worsening" if delta > 2 else ("improving" if delta < -2 else "stable")

    return RiskPredictionResult(
        current_risk=round(current_risk, 1), predicted_risk=round(predicted_risk, 1),
        risk_category=_risk_category(predicted_risk), confidence=round(confidence, 2),
        trend_direction=trend_direction, insufficient_data=False,
        feature_vector=features[0].tolist(),
    )
