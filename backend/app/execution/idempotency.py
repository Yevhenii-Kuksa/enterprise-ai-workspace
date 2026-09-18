import hashlib
import uuid


def calculate_execution_idempotency_key(
    *,
    organization_id: uuid.UUID,
    proposal_id: uuid.UUID,
    proposal_fingerprint: str,
    action_type: str,
) -> str:
    value = ":".join(
        (
            str(organization_id),
            str(proposal_id),
            proposal_fingerprint,
            action_type,
        )
    )

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()