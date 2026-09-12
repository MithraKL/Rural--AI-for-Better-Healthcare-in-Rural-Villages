"""Signature feature — Infrastructure-Outcome Paradox detector.

Flags villages where infrastructure availability is relatively adequate but
service utilization / delivery / outcomes remain poor — i.e. infrastructure
existing on paper is not translating into effective healthcare delivery.

This module never claims causality. Output language is deliberately hedged
("possible contributing factors", "requires field validation").
"""
from dataclasses import dataclass
from backend.services.gap_index import GapIndexResult

INFRA_HIGH_THRESHOLD = 65.0
WEAK_DIMENSION_THRESHOLD = 45.0


@dataclass
class ParadoxResult:
    is_paradox: bool
    note: str | None


def detect_paradox(scores: GapIndexResult) -> ParadoxResult:
    weak_dims = []
    if scores.service_score <= WEAK_DIMENSION_THRESHOLD:
        weak_dims.append(("service delivery", scores.service_score))
    if scores.utilization_score <= WEAK_DIMENSION_THRESHOLD:
        weak_dims.append(("healthcare utilization", scores.utilization_score))
    if scores.outcome_score <= WEAK_DIMENSION_THRESHOLD:
        weak_dims.append(("health outcomes", scores.outcome_score))
    if scores.nutrition_score <= WEAK_DIMENSION_THRESHOLD:
        weak_dims.append(("nutrition indicators", scores.nutrition_score))

    is_paradox = scores.infrastructure_score >= INFRA_HIGH_THRESHOLD and len(weak_dims) >= 2

    if not is_paradox:
        return ParadoxResult(is_paradox=False, note=None)

    weak_names = ", ".join(name for name, _ in weak_dims)
    note = (
        f"Hidden Healthcare Gap: infrastructure availability is relatively adequate "
        f"(Infrastructure Score {scores.infrastructure_score:.0f}/100), but {weak_names} "
        f"remain poor. Possible contributing factors include low community awareness, "
        f"staff behavior or availability at point of care, service timing mismatches, or "
        f"demand-side barriers. This is an associated-indicator pattern, not a confirmed "
        f"cause — it requires field validation before action is taken."
    )
    return ParadoxResult(is_paradox=True, note=note)
