from app.approvals.fingerprint import (
    calculate_proposal_fingerprint,
    canonicalize_snapshot,
    verify_proposal_fingerprint,
)
from app.approvals.schemas import ApprovalProposalSnapshot


def make_snapshot() -> ApprovalProposalSnapshot:
    return ApprovalProposalSnapshot(
        action_type="order.update",
        resource_type="order",
        resource_id="ORD-001",
        payload={
            "status": "confirmed",
            "priority": "high",
        },
        justification="Zmiana wymaga zatwierdzenia przez uprawnioną osobę.",
    )


def test_fingerprint_is_deterministic() -> None:
    snapshot = make_snapshot()

    first = calculate_proposal_fingerprint(snapshot)
    second = calculate_proposal_fingerprint(snapshot)

    assert first == second
    assert len(first) == 64


def test_fingerprint_is_independent_of_payload_key_order() -> None:
    first = ApprovalProposalSnapshot(
        action_type="order.update",
        resource_type="order",
        resource_id="ORD-001",
        payload={
            "status": "confirmed",
            "priority": "high",
        },
        justification="Test",
    )

    second = ApprovalProposalSnapshot(
        action_type="order.update",
        resource_type="order",
        resource_id="ORD-001",
        payload={
            "priority": "high",
            "status": "confirmed",
        },
        justification="Test",
    )

    assert calculate_proposal_fingerprint(
        first
    ) == calculate_proposal_fingerprint(second)


def test_fingerprint_changes_when_snapshot_changes() -> None:
    original = make_snapshot()

    changed = original.model_copy(
        update={
            "payload": {
                "status": "cancelled",
                "priority": "high",
            }
        }
    )

    assert calculate_proposal_fingerprint(
        original
    ) != calculate_proposal_fingerprint(changed)


def test_verify_fingerprint_accepts_unchanged_snapshot() -> None:
    snapshot = make_snapshot()
    fingerprint = calculate_proposal_fingerprint(snapshot)

    assert verify_proposal_fingerprint(
        snapshot,
        fingerprint,
    )


def test_verify_fingerprint_rejects_modified_snapshot() -> None:
    snapshot = make_snapshot()
    fingerprint = calculate_proposal_fingerprint(snapshot)

    modified = snapshot.model_copy(
        update={
            "resource_id": "ORD-002",
        }
    )

    assert not verify_proposal_fingerprint(
        modified,
        fingerprint,
    )


def test_canonical_snapshot_is_deterministic() -> None:
    snapshot = make_snapshot()

    canonical = canonicalize_snapshot(snapshot)

    assert canonical == canonicalize_snapshot(snapshot)
    assert '"action_type":"order.update"' in canonical
    assert '"resource_id":"ORD-001"' in canonical