"""Module 4 — Village Prioritization.

Ranks villages by more than raw risk: combines predicted risk, population
affected, severity (overall gap score) and trend direction into a single
Priority Score, so officials can answer "where should we intervene first?"
"""
from dataclasses import dataclass

WEIGHTS = {"risk": 0.45, "population": 0.25, "severity": 0.15, "trend": 0.15}


@dataclass
class PriorityInput:
    village_id: int
    predicted_risk: float
    overall_gap_score: float
    population: int
    trend_delta: float  # predicted_risk - current_risk; positive = worsening


@dataclass
class PriorityOutput:
    village_id: int
    priority_score: float
    priority_tier: str
    population_affected: int
    rank: int = 0


def _tier(score: float) -> str:
    if score >= 58:
        return "CRITICAL"
    if score >= 42:
        return "HIGH"
    if score >= 28:
        return "MODERATE"
    return "LOW"


def compute_priorities(inputs: list[PriorityInput]) -> list[PriorityOutput]:
    if not inputs:
        return []
    max_pop = max((i.population for i in inputs), default=1) or 1

    results = []
    for i in inputs:
        risk_norm = min(i.predicted_risk / 100.0, 1.0)
        pop_norm = min(i.population / max_pop, 1.0)
        severity_norm = min(i.overall_gap_score / 100.0, 1.0)
        trend_norm = min(max(i.trend_delta, 0) / 30.0, 1.0)

        score = 100 * (
            WEIGHTS["risk"] * risk_norm
            + WEIGHTS["population"] * pop_norm
            + WEIGHTS["severity"] * severity_norm
            + WEIGHTS["trend"] * trend_norm
        )
        results.append(PriorityOutput(
            village_id=i.village_id,
            priority_score=round(score, 1),
            priority_tier=_tier(score),
            population_affected=i.population,
        ))

    results.sort(key=lambda r: r.priority_score, reverse=True)
    for idx, r in enumerate(results, start=1):
        r.rank = idx
    return results
