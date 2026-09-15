from dataclasses import dataclass
from enum import StrEnum


class SufficiencyStatus(StrEnum):
    SUFFICIENT = "sufficient"
    INSUFFICIENT = "insufficient"


@dataclass(frozen=True, slots=True)
class SufficiencyResult:
    status: SufficiencyStatus
    evidence_count: int
    qualifying_evidence_count: int


def evaluate_sufficiency(
    *,
    distances: list[float],
    max_distance: float,
) -> SufficiencyResult:
    if max_distance < 0:
        raise ValueError(
            "Maximum evidence distance must not be negative."
        )

    qualifying_evidence_count = sum(
        distance <= max_distance
        for distance in distances
    )

    status = (
        SufficiencyStatus.SUFFICIENT
        if qualifying_evidence_count > 0
        else SufficiencyStatus.INSUFFICIENT
    )

    return SufficiencyResult(
        status=status,
        evidence_count=len(distances),
        qualifying_evidence_count=qualifying_evidence_count,
    )