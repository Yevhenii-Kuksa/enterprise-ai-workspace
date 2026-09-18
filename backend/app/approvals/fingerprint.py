import hashlib
import json
from typing import Any

from app.approvals.schemas import ApprovalProposalSnapshot


def canonicalize_snapshot(
    snapshot: ApprovalProposalSnapshot,
) -> str:
    data: dict[str, Any] = snapshot.model_dump(mode="json")

    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def calculate_proposal_fingerprint(
    snapshot: ApprovalProposalSnapshot,
) -> str:
    canonical_snapshot = canonicalize_snapshot(snapshot)

    return hashlib.sha256(
        canonical_snapshot.encode("utf-8")
    ).hexdigest()


def verify_proposal_fingerprint(
    snapshot: ApprovalProposalSnapshot,
    fingerprint: str,
) -> bool:
    expected = calculate_proposal_fingerprint(snapshot)

    return expected == fingerprint