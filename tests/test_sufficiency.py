from app.ai.reliability.sufficiency import (
    SufficiencyStatus,
    evaluate_sufficiency,
)


def test_sufficiency_is_insufficient_without_evidence() -> None:
    result = evaluate_sufficiency(
        distances=[],
        max_distance=0.35,
    )

    assert result.status is SufficiencyStatus.INSUFFICIENT
    assert result.evidence_count == 0
    assert result.qualifying_evidence_count == 0


def test_sufficiency_is_sufficient_with_relevant_evidence() -> None:
    result = evaluate_sufficiency(
        distances=[0.12, 0.28, 0.61],
        max_distance=0.35,
    )

    assert result.status is SufficiencyStatus.SUFFICIENT
    assert result.evidence_count == 3
    assert result.qualifying_evidence_count == 2


def test_sufficiency_is_insufficient_with_only_weak_evidence() -> None:
    result = evaluate_sufficiency(
        distances=[0.48, 0.61, 0.79],
        max_distance=0.35,
    )

    assert result.status is SufficiencyStatus.INSUFFICIENT
    assert result.evidence_count == 3
    assert result.qualifying_evidence_count == 0


def test_sufficiency_accepts_distance_equal_to_threshold() -> None:
    result = evaluate_sufficiency(
        distances=[0.35],
        max_distance=0.35,
    )

    assert result.status is SufficiencyStatus.SUFFICIENT
    assert result.qualifying_evidence_count == 1


def test_sufficiency_rejects_invalid_max_distance() -> None:
    try:
        evaluate_sufficiency(
            distances=[0.1],
            max_distance=-0.1,
        )
    except ValueError as exc:
        assert str(exc) == (
            "Maximum evidence distance must not be negative."
        )
    else:
        raise AssertionError("Expected ValueError.")