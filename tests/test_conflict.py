from app.ai.reliability.conflict import (
    ConflictStatus,
    evaluate_conflict,
)


def test_conflict_is_unknown_when_not_checked() -> None:
    result = evaluate_conflict(
        conflict_count=0,
        checked=False,
    )

    assert result.status is ConflictStatus.UNKNOWN
    assert result.conflict_count == 0
    assert result.checked is False


def test_conflict_is_none_when_checked_without_conflicts() -> None:
    result = evaluate_conflict(
        conflict_count=0,
        checked=True,
    )

    assert result.status is ConflictStatus.NONE
    assert result.conflict_count == 0
    assert result.checked is True


def test_conflict_is_detected_when_conflicts_exist() -> None:
    result = evaluate_conflict(
        conflict_count=2,
        checked=True,
    )

    assert result.status is ConflictStatus.DETECTED
    assert result.conflict_count == 2
    assert result.checked is True


def test_conflict_ignores_untrusted_count_when_not_checked() -> None:
    result = evaluate_conflict(
        conflict_count=3,
        checked=False,
    )

    assert result.status is ConflictStatus.UNKNOWN
    assert result.conflict_count == 0
    assert result.checked is False


def test_conflict_rejects_negative_count() -> None:
    try:
        evaluate_conflict(
            conflict_count=-1,
            checked=True,
        )
    except ValueError as exc:
        assert str(exc) == (
            "Conflict count must not be negative."
        )
    else:
        raise AssertionError("Expected ValueError.")