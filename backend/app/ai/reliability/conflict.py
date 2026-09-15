from dataclasses import dataclass
from enum import StrEnum


class ConflictStatus(StrEnum):
    NONE = "none"
    DETECTED = "detected"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ConflictResult:
    status: ConflictStatus
    conflict_count: int
    checked: bool


def evaluate_conflict(
    *,
    conflict_count: int,
    checked: bool,
) -> ConflictResult:
    if conflict_count < 0:
        raise ValueError(
            "Conflict count must not be negative."
        )

    if not checked:
        return ConflictResult(
            status=ConflictStatus.UNKNOWN,
            conflict_count=0,
            checked=False,
        )

    status = (
        ConflictStatus.DETECTED
        if conflict_count > 0
        else ConflictStatus.NONE
    )

    return ConflictResult(
        status=status,
        conflict_count=conflict_count,
        checked=True,
    )