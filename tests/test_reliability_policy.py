from app.ai.reliability.conflict import (
    ConflictResult,
    ConflictStatus,
)
from app.ai.reliability.freshness import (
    FreshnessResult,
    FreshnessStatus,
)
from app.ai.reliability.policy import (
    ReliabilityDecision,
    evaluate_reliability_policy,
)
from app.ai.reliability.service import ReliabilityResult
from app.ai.reliability.sufficiency import (
    SufficiencyResult,
    SufficiencyStatus,
)


def _build_result(
    *,
    sufficiency: SufficiencyStatus = SufficiencyStatus.SUFFICIENT,
    freshness: FreshnessStatus = FreshnessStatus.FRESH,
    conflict: ConflictStatus = ConflictStatus.NONE,
) -> ReliabilityResult:
    return ReliabilityResult(
        sufficiency=SufficiencyResult(
            status=sufficiency,
            evidence_count=2,
            qualifying_evidence_count=2,
        ),
        freshness=FreshnessResult(
            status=freshness,
            source_count=2,
            fresh_source_count=2,
            stale_source_count=0,
            unknown_source_count=0,
        ),
        conflict=ConflictResult(
            status=conflict,
            conflict_count=(
                1
                if conflict is ConflictStatus.DETECTED
                else 0
            ),
            checked=conflict is not ConflictStatus.UNKNOWN,
        ),
    )


def test_policy_allows_reliable_context() -> None:
    result = evaluate_reliability_policy(
        _build_result()
    )

    assert result.decision is ReliabilityDecision.ALLOW
    assert result.reasons == ()


def test_policy_refuses_insufficient_evidence() -> None:
    result = evaluate_reliability_policy(
        _build_result(
            sufficiency=SufficiencyStatus.INSUFFICIENT,
        )
    )

    assert result.decision is ReliabilityDecision.REFUSE
    assert result.reasons == ("insufficient_evidence",)


def test_policy_refuses_detected_conflict() -> None:
    result = evaluate_reliability_policy(
        _build_result(
            conflict=ConflictStatus.DETECTED,
        )
    )

    assert result.decision is ReliabilityDecision.REFUSE
    assert result.reasons == ("conflict_detected",)


def test_policy_refuses_multiple_blocking_reasons() -> None:
    result = evaluate_reliability_policy(
        _build_result(
            sufficiency=SufficiencyStatus.INSUFFICIENT,
            conflict=ConflictStatus.DETECTED,
        )
    )

    assert result.decision is ReliabilityDecision.REFUSE
    assert result.reasons == (
        "insufficient_evidence",
        "conflict_detected",
    )


def test_policy_degrades_stale_sources() -> None:
    result = evaluate_reliability_policy(
        _build_result(
            freshness=FreshnessStatus.STALE,
        )
    )

    assert result.decision is ReliabilityDecision.DEGRADE
    assert result.reasons == ("stale_sources",)


def test_policy_degrades_unknown_freshness() -> None:
    result = evaluate_reliability_policy(
        _build_result(
            freshness=FreshnessStatus.UNKNOWN,
        )
    )

    assert result.decision is ReliabilityDecision.DEGRADE
    assert result.reasons == ("unknown_source_freshness",)


def test_policy_degrades_when_conflict_was_not_checked() -> None:
    result = evaluate_reliability_policy(
        _build_result(
            conflict=ConflictStatus.UNKNOWN,
        )
    )

    assert result.decision is ReliabilityDecision.DEGRADE
    assert result.reasons == ("conflict_not_checked",)


def test_policy_collects_multiple_degrade_reasons() -> None:
    result = evaluate_reliability_policy(
        _build_result(
            freshness=FreshnessStatus.UNKNOWN,
            conflict=ConflictStatus.UNKNOWN,
        )
    )

    assert result.decision is ReliabilityDecision.DEGRADE
    assert result.reasons == (
        "unknown_source_freshness",
        "conflict_not_checked",
    )