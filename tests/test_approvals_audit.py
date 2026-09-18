import uuid
from datetime import UTC, datetime

import pytest
from app.approvals.dependencies import get_approval_service
from app.approvals.schemas import (
    ApprovalProposalCreate,
    ApprovalProposalSnapshot,
    ApprovalStatus,
)
from app.db.dependencies import get_db
from app.main import app
from app.models.approval_proposal import ApprovalProposal
from app.security.current_user import CurrentUser
from app.security.dependencies import get_current_user
from fastapi.testclient import TestClient

ORGANIZATION_ID = uuid.uuid4()
AUTHOR_ID = uuid.uuid4()
REVIEWER_ID = uuid.uuid4()
PROPOSAL_ID = uuid.uuid4()
CREATED_AT = datetime(2026, 9, 18, 12, 0, tzinfo=UTC)


class FakeDb:
    def __init__(self) -> None:
        self.added: list[object] = []

    def add(self, obj: object) -> None:
        self.added.append(obj)

    def flush(self) -> None:
        pass

    def commit(self) -> None:
        pass

    def refresh(self, _object: object) -> None:
        pass


class FakeApprovalService:
    def __init__(self) -> None:
        self.proposal = _proposal()

    def create(
        self,
        *,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        data: ApprovalProposalCreate,
    ) -> ApprovalProposal:
        assert organization_id == ORGANIZATION_ID
        assert user_id == AUTHOR_ID
        assert data.action_type == "order.update"
        return self.proposal

    def approve(
        self,
        *,
        organization_id: uuid.UUID,
        proposal_id: uuid.UUID,
        user_id: uuid.UUID,
        comment: str | None = None,
    ) -> ApprovalProposal:
        assert organization_id == ORGANIZATION_ID
        assert proposal_id == PROPOSAL_ID

        self.proposal.status = ApprovalStatus.APPROVED.value
        self.proposal.decided_by_user_id = user_id
        self.proposal.decided_at = datetime.now(UTC)
        self.proposal.decision_comment = comment

        return self.proposal

    def reject(
        self,
        *,
        organization_id: uuid.UUID,
        proposal_id: uuid.UUID,
        user_id: uuid.UUID,
        comment: str | None = None,
    ) -> ApprovalProposal:
        assert organization_id == ORGANIZATION_ID
        assert proposal_id == PROPOSAL_ID

        self.proposal.status = ApprovalStatus.REJECTED.value
        self.proposal.decided_by_user_id = user_id
        self.proposal.decided_at = datetime.now(UTC)
        self.proposal.decision_comment = comment

        return self.proposal

    def cancel(
        self,
        *,
        organization_id: uuid.UUID,
        proposal_id: uuid.UUID,
        comment: str | None = None,
    ) -> ApprovalProposal:
        assert organization_id == ORGANIZATION_ID
        assert proposal_id == PROPOSAL_ID

        self.proposal.status = ApprovalStatus.CANCELLED.value
        self.proposal.decided_at = datetime.now(UTC)
        self.proposal.decision_comment = comment

        return self.proposal


def _proposal() -> ApprovalProposal:
    snapshot = ApprovalProposalSnapshot(
        action_type="order.update",
        resource_type="order",
        resource_id="ORDER-001",
        payload={"status": "confirmed"},
        justification="Zmiana wymaga zatwierdzenia.",
    )

    return ApprovalProposal(
        id=PROPOSAL_ID,
        organization_id=ORGANIZATION_ID,
        created_by_user_id=AUTHOR_ID,
        status=ApprovalStatus.PENDING.value,
        action_type=snapshot.action_type,
        resource_type=snapshot.resource_type,
        resource_id=snapshot.resource_id,
        payload=snapshot.payload,
        justification=snapshot.justification,
        snapshot=snapshot.model_dump(mode="json"),
        fingerprint="a" * 64,
        created_at=CREATED_AT,
        expires_at=None,
        decided_by_user_id=None,
        decided_at=None,
        decision_comment=None,
    )


def _user(
    *,
    user_id: uuid.UUID,
    permission: str,
) -> CurrentUser:
    return CurrentUser(
        id=user_id,
        organization_id=ORGANIZATION_ID,
        is_active=True,
        permissions={permission},
    )


@pytest.mark.parametrize(
    ("operation", "permission", "user_id", "event_type"),
    [
        (
            "create",
            "approval.create",
            AUTHOR_ID,
            "approval_created",
        ),
        (
            "approve",
            "approval.decide",
            REVIEWER_ID,
            "approval_approved",
        ),
        (
            "reject",
            "approval.decide",
            REVIEWER_ID,
            "approval_rejected",
        ),
        (
            "cancel",
            "approval.cancel",
            AUTHOR_ID,
            "approval_cancelled",
        ),
    ],
)
def test_approval_operation_creates_audit_event(
    operation: str,
    permission: str,
    user_id: uuid.UUID,
    event_type: str,
) -> None:
    fake_db = FakeDb()
    service = FakeApprovalService()

    def override_db() -> FakeDb:
        return fake_db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: _user(
        user_id=user_id,
        permission=permission,
    )
    app.dependency_overrides[get_approval_service] = lambda: service

    try:
        client = TestClient(app)

        if operation == "create":
            response = client.post(
                "/api/approvals",
                json={
                    "action_type": "order.update",
                    "resource_type": "order",
                    "resource_id": "ORDER-001",
                    "payload": {
                        "status": "confirmed",
                    },
                    "justification": (
                        "Zmiana wymaga zatwierdzenia."
                    ),
                },
            )
        else:
            response = client.post(
                f"/api/approvals/{PROPOSAL_ID}/{operation}",
                json={"comment": "Test decyzji."},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code in {200, 201}
    assert len(fake_db.added) == 1

    event = fake_db.added[0]

    assert event.event_type == event_type
    assert event.organization_id == ORGANIZATION_ID
    assert event.user_id == user_id
    assert event.resource_type == "approval_proposal"
    assert event.resource_id == str(PROPOSAL_ID)

    assert event.trace_id is not None
    assert event.request_id is not None

    assert event.metadata_json["action_type"] == "order.update"
    assert event.metadata_json["target_resource_type"] == "order"
    assert event.metadata_json["target_resource_id"] == "ORDER-001"