from datetime import UTC, datetime, timedelta

from app.ai.reliability.freshness import (
    FreshnessStatus,
    evaluate_freshness,
)

EVALUATED_AT = datetime(
    2026,
    9,
    15,
    12,
    0,
    tzinfo=UTC,
)


def test_freshness_is_fresh_when_all_known_sources_are_recent() -> None:
    result = evaluate_freshness(
        source_modified_at=[
            EVALUATED_AT - timedelta(days=2),
            EVALUATED_AT - timedelta(days=10),
        ],
        evaluated_at=EVALUATED_AT,
        max_age=timedelta(days=30),
    )

    assert result.status is FreshnessStatus.FRESH
    assert result.source_count == 2
    assert result.fresh_source_count == 2
    assert result.stale_source_count == 0
    assert result.unknown_source_count == 0


def test_freshness_is_stale_when_any_source_is_too_old() -> None:
    result = evaluate_freshness(
        source_modified_at=[
            EVALUATED_AT - timedelta(days=5),
            EVALUATED_AT - timedelta(days=45),
        ],
        evaluated_at=EVALUATED_AT,
        max_age=timedelta(days=30),
    )

    assert result.status is FreshnessStatus.STALE
    assert result.source_count == 2
    assert result.fresh_source_count == 1
    assert result.stale_source_count == 1
    assert result.unknown_source_count == 0


def test_freshness_is_unknown_without_source_timestamp() -> None:
    result = evaluate_freshness(
        source_modified_at=[None],
        evaluated_at=EVALUATED_AT,
        max_age=timedelta(days=30),
    )

    assert result.status is FreshnessStatus.UNKNOWN
    assert result.source_count == 1
    assert result.fresh_source_count == 0
    assert result.stale_source_count == 0
    assert result.unknown_source_count == 1


def test_freshness_is_unknown_for_mixed_known_and_unknown_sources() -> None:
    result = evaluate_freshness(
        source_modified_at=[
            EVALUATED_AT - timedelta(days=5),
            None,
        ],
        evaluated_at=EVALUATED_AT,
        max_age=timedelta(days=30),
    )

    assert result.status is FreshnessStatus.UNKNOWN
    assert result.source_count == 2
    assert result.fresh_source_count == 1
    assert result.stale_source_count == 0
    assert result.unknown_source_count == 1


def test_freshness_treats_threshold_age_as_fresh() -> None:
    result = evaluate_freshness(
        source_modified_at=[
            EVALUATED_AT - timedelta(days=30),
        ],
        evaluated_at=EVALUATED_AT,
        max_age=timedelta(days=30),
    )

    assert result.status is FreshnessStatus.FRESH
    assert result.fresh_source_count == 1


def test_freshness_rejects_negative_max_age() -> None:
    try:
        evaluate_freshness(
            source_modified_at=[],
            evaluated_at=EVALUATED_AT,
            max_age=timedelta(seconds=-1),
        )
    except ValueError as exc:
        assert str(exc) == (
            "Maximum source age must not be negative."
        )
    else:
        raise AssertionError("Expected ValueError.")