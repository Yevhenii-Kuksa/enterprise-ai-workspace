from dataclasses import dataclass
from enum import StrEnum

from app.ai.reliability.conflict import ConflictStatus
from app.ai.reliability.freshness import FreshnessStatus
from app.ai.reliability.service import ReliabilityResult
from app.ai.reliability.sufficiency import SufficiencyStatus


class ReliabilityDecision(StrEnum):
    ALLOW = "allow"
    DEGRADE = "degrade"
    REFUSE = "refuse"


@dataclass(frozen=True, slots=True)
class ReliabilityPolicyResult:
    decision: ReliabilityDecision
    reasons: tuple[str, ...]


def evaluate_reliability_policy(
    result: ReliabilityResult,
) -> ReliabilityPolicyResult:
    reasons: list[str] = []

    if result.sufficiency.status is SufficiencyStatus.INSUFFICIENT:
        reasons.append("insufficient_evidence")

    if result.conflict.status is ConflictStatus.DETECTED:
        reasons.append("conflict_detected")

    if reasons:
        return ReliabilityPolicyResult(
            decision=ReliabilityDecision.REFUSE,
            reasons=tuple(reasons),
        )

    if result.freshness.status is FreshnessStatus.STALE:
        reasons.append("stale_sources")

    if result.freshness.status is FreshnessStatus.UNKNOWN:
        reasons.append("unknown_source_freshness")

    if result.conflict.status is ConflictStatus.UNKNOWN:
        reasons.append("conflict_not_checked")

    if reasons:
        return ReliabilityPolicyResult(
            decision=ReliabilityDecision.DEGRADE,
            reasons=tuple(reasons),
        )

    return ReliabilityPolicyResult(
        decision=ReliabilityDecision.ALLOW,
        reasons=(),
    )