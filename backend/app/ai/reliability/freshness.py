from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum


class FreshnessStatus(StrEnum):
    FRESH = "fresh"
    STALE = "stale"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class FreshnessResult:
    status: FreshnessStatus
    source_count: int
    fresh_source_count: int
    stale_source_count: int
    unknown_source_count: int


def evaluate_freshness(
    *,
    source_modified_at: list[datetime | None],
    evaluated_at: datetime,
    max_age: timedelta,
) -> FreshnessResult:
    if max_age < timedelta(0):
        raise ValueError(
            "Maximum source age must not be negative."
        )

    fresh_source_count = 0
    stale_source_count = 0
    unknown_source_count = 0

    for modified_at in source_modified_at:
        if modified_at is None:
            unknown_source_count += 1
            continue

        age = evaluated_at - modified_at

        if age <= max_age:
            fresh_source_count += 1
        else:
            stale_source_count += 1

    if stale_source_count > 0:
        status = FreshnessStatus.STALE
    elif unknown_source_count > 0:
        status = FreshnessStatus.UNKNOWN
    else:
        status = FreshnessStatus.FRESH

    return FreshnessResult(
        status=status,
        source_count=len(source_modified_at),
        fresh_source_count=fresh_source_count,
        stale_source_count=stale_source_count,
        unknown_source_count=unknown_source_count,
    )