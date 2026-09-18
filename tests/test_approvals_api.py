import uuid
from datetime import UTC, datetime

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
OTHER_ORGANIZATION_ID = uuid.uuid4()
AUTHOR_ID = uuid.uuid4()
REVIEWER_ID = uuid.uuid4()
PROPOSAL_ID = uuid.uuid4()
CREATED_AT = datetime(2026, 9, 18, 12, 0, tzinfo=UTC)


class FakeDb:
    def add(self, _object: object) -> None:
        pass

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

    def list(
        self,
        *,
        organization_id: uuid.UUID,
        status: ApprovalStatus | None = None,
    ) -> list[ApprovalProposal]:
        if organization_id != ORGANIZATION_ID:
            return []

        if status is not None and self.proposal.status != status.value:
            return []

        return [self.proposal]

    def get(
        self,
        *,
        organization_id: uuid.UUID,
        proposal_id: uuid.UUID,
    ) -> ApprovalProposal:
        from app.approvals.service import ApprovalNotFoundError

        if (
            organization_id != ORGANIZATION_ID
            or proposal_id != PROPOSAL_ID
        ):
            raise ApprovalNotFoundError(
                "Approval proposal not found."
            )

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
        assert user_id == REVIEWER_ID

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
        assert user_id == REVIEWER_ID

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
    organization_id: uuid.UUID = ORGANIZATION_ID,
    permissions: set[str],
) -> CurrentUser:
    return CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions=permissions,
    )


def _override_db() -> FakeDb:
    return FakeDb()


def _run_with_overrides(
    *,
    user: CurrentUser,
    service: FakeApprovalService,
) -> TestClient:
    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_approval_service] = lambda: service
    return TestClient(app)


def test_create_approval() -> None:
    service = FakeApprovalService()
    user = _user(
        user_id=AUTHOR_ID,
        permissions={"approval.create"},
    )

    try:
        client = _run_with_overrides(
            user=user,
            service=service,
        )

        response = client.post(
            "/api/approvals",
            json={
                "action_type": "order.update",
                "resource_type": "order",
                "resource_id": "ORDER-001",
                "payload": {"status": "confirmed"},
                "justification": "Zmiana wymaga zatwierdzenia.",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["id"] == str(PROPOSAL_ID)
    assert response.json()["status"] == "pending"
    assert response.json()["organization_id"] == str(ORGANIZATION_ID)


def test_list_approvals() -> None:
    service = FakeApprovalService()
    user = _user(
        user_id=AUTHOR_ID,
        permissions={"approval.read"},
    )

    try:
        client = _run_with_overrides(
            user=user,
            service=service,
        )
        response = client.get("/api/approvals")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == str(PROPOSAL_ID)


def test_get_approval() -> None:
    service = FakeApprovalService()
    user = _user(
        user_id=AUTHOR_ID,
        permissions={"approval.read"},
    )

    try:
        client = _run_with_overrides(
            user=user,
            service=service,
        )
        response = client.get(
            f"/api/approvals/{PROPOSAL_ID}"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["id"] == str(PROPOSAL_ID)


def test_get_approval_is_tenant_isolated() -> None:
    service = FakeApprovalService()
    user = _user(
        user_id=uuid.uuid4(),
        organization_id=OTHER_ORGANIZATION_ID,
        permissions={"approval.read"},
    )

    try:
        client = _run_with_overrides(
            user=user,
            service=service,
        )
        response = client.get(
            f"/api/approvals/{PROPOSAL_ID}"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404


def test_approve_approval() -> None:
    service = FakeApprovalService()
    user = _user(
        user_id=REVIEWER_ID,
        permissions={"approval.decide"},
    )

    try:
        client = _run_with_overrides(
            user=user,
            service=service,
        )
        response = client.post(
            f"/api/approvals/{PROPOSAL_ID}/approve",
            json={"comment": "Zatwierdzono."},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    assert response.json()["decided_by_user_id"] == str(REVIEWER_ID)


def test_reject_approval() -> None:
    service = FakeApprovalService()
    user = _user(
        user_id=REVIEWER_ID,
        permissions={"approval.decide"},
    )

    try:
        client = _run_with_overrides(
            user=user,
            service=service,
        )
        response = client.post(
            f"/api/approvals/{PROPOSAL_ID}/reject",
            json={"comment": "Odrzucono."},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


def test_cancel_approval() -> None:
    service = FakeApprovalService()
    user = _user(
        user_id=AUTHOR_ID,
        permissions={"approval.cancel"},
    )

    try:
        client = _run_with_overrides(
            user=user,
            service=service,
        )
        response = client.post(
            f"/api/approvals/{PROPOSAL_ID}/cancel",
            json={"comment": "Anulowano."},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_create_requires_permission() -> None:
    service = FakeApprovalService()
    user = _user(
        user_id=AUTHOR_ID,
        permissions=set(),
    )

    try:
        client = _run_with_overrides(
            user=user,
            service=service,
        )
        response = client.post(
            "/api/approvals",
            json={
                "action_type": "order.update",
                "resource_type": "order",
                "resource_id": "ORDER-001",
                "payload": {},
                "justification": "Test.",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403


def test_read_requires_permission() -> None:
    service = FakeApprovalService()
    user = _user(
        user_id=AUTHOR_ID,
        permissions=set(),
    )

    try:
        client = _run_with_overrides(
            user=user,
            service=service,
        )
        response = client.get("/api/approvals")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403


def test_decide_requires_permission() -> None:
    service = FakeApprovalService()
    user = _user(
        user_id=REVIEWER_ID,
        permissions=set(),
    )

    try:
        client = _run_with_overrides(
            user=user,
            service=service,
        )
        response = client.post(
            f"/api/approvals/{PROPOSAL_ID}/approve",
            json={},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403


def test_cancel_requires_permission() -> None:
    service = FakeApprovalService()
    user = _user(
        user_id=AUTHOR_ID,
        permissions=set(),
    )

    try:
        client = _run_with_overrides(
            user=user,
            service=service,
        )
        response = client.post(
            f"/api/approvals/{PROPOSAL_ID}/cancel",
            json={},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403