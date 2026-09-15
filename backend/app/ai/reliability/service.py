from dataclasses import dataclass
from datetime import datetime, timedelta

from app.ai.reliability.conflict import (
    ConflictResult,
    evaluate_conflict,
)
from app.ai.reliability.freshness import (
    FreshnessResult,
    evaluate_freshness,
)
from app.ai.reliability.sufficiency import (
    SufficiencyResult,
    evaluate_sufficiency,
)
from app.retrieval.context import RagContext


@dataclass(frozen=True, slots=True)
class ReliabilityResult:
    sufficiency: SufficiencyResult
    freshness: FreshnessResult
    conflict: ConflictResult


def evaluate_reliability(
    *,
    context: RagContext,
    evaluated_at: datetime,
    max_evidence_distance: float,
    max_source_age: timedelta,
    conflict_count: int = 0,
    conflict_checked: bool = False,
) -> ReliabilityResult:
    distances = [
        source.evidence.distance
        for source in context.sources
    ]

    source_modified_at = [
        source.evidence.source_modified_at
        for source in context.sources
    ]

    sufficiency = evaluate_sufficiency(
        distances=distances,
        max_distance=max_evidence_distance,
    )

    freshness = evaluate_freshness(
        source_modified_at=source_modified_at,
        evaluated_at=evaluated_at,
        max_age=max_source_age,
    )

    conflict = evaluate_conflict(
        conflict_count=conflict_count,
        checked=conflict_checked,
    )

    return ReliabilityResult(
        sufficiency=sufficiency,
        freshness=freshness,
        conflict=conflict,
    )