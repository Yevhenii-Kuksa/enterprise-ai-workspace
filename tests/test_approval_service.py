import uuid
from datetime import UTC, datetime, timedelta

import pytest
from app.approvals.schemas import (
    ApprovalProposalCreate,
    ApprovalStatus,
)
from app.approvals.service import (
    ApprovalFingerprintError,
    ApprovalInvalidStateError,
    ApprovalNotFoundError,
    ApprovalSeparationOfDutiesError,
    ApprovalService,
)
from app.db.session import SessionLocal
from app.models.organization import Organization
from app.models.user import User


def add_organization(
    db: object,
    organization_id: uuid.UUID,
) -> None:
    db.add(
        Organization(
            id=organization_id,
            code=f"APPROVAL-{organization_id.hex[:8]}",
            name="Approval Test Organization",
        )
    )


def add_user(
    db: object,
    *,
    user_id: uuid.UUID,
    organization_id: uuid.UUID,
) -> None:
    db.add(
        User(
            id=user_id,
            organization_id=organization_id,
            email=f"{user_id.hex}@example.com",
            full_name="Approval Test User",
        )
    )


def proposal_data(
    *,
    expires_at: datetime | None = None,
) -> ApprovalProposalCreate:
    return ApprovalProposalCreate(
        action_type="order.update",
        resource_type="order",
        resource_id="ORDER-001",
        payload={
            "status": "confirmed",
            "priority": "high",
        },
        justification="Zmiana wymaga zatwierdzenia.",
        expires_at=expires_at,
    )


def test_create_proposal() -> None:
    organization_id = uuid.uuid4()
    author_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)
        add_user(
            db,
            user_id=author_id,
            organization_id=organization_id,
        )
        db.flush()

        service = ApprovalService(db)

        proposal = service.create(
            organization_id=organization_id,
            user_id=author_id,
            data=proposal_data(),
        )

        assert proposal.organization_id == organization_id
        assert proposal.created_by_user_id == author_id
        assert proposal.status == ApprovalStatus.PENDING.value
        assert len(proposal.fingerprint) == 64
        assert proposal.snapshot["action_type"] == "order.update"

        db.rollback()


def test_get_is_tenant_isolated() -> None:
    organization_id = uuid.uuid4()
    other_organization_id = uuid.uuid4()
    author_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)
        add_organization(db, other_organization_id)
        add_user(
            db,
            user_id=author_id,
            organization_id=organization_id,
        )
        db.flush()

        service = ApprovalService(db)

        proposal = service.create(
            organization_id=organization_id,
            user_id=author_id,
            data=proposal_data(),
        )

        with pytest.raises(ApprovalNotFoundError):
            service.get(
                organization_id=other_organization_id,
                proposal_id=proposal.id,
            )

        db.rollback()


def test_approve_proposal() -> None:
    organization_id = uuid.uuid4()
    author_id = uuid.uuid4()
    approver_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)
        add_user(
            db,
            user_id=author_id,
            organization_id=organization_id,
        )
        add_user(
            db,
            user_id=approver_id,
            organization_id=organization_id,
        )
        db.flush()

        service = ApprovalService(db)

        proposal = service.create(
            organization_id=organization_id,
            user_id=author_id,
            data=proposal_data(),
        )

        result = service.approve(
            organization_id=organization_id,
            proposal_id=proposal.id,
            user_id=approver_id,
            comment="Zatwierdzono.",
        )

        assert result.status == ApprovalStatus.APPROVED.value
        assert result.decided_by_user_id == approver_id
        assert result.decided_at is not None
        assert result.decision_comment == "Zatwierdzono."

        db.rollback()


def test_reject_proposal() -> None:
    organization_id = uuid.uuid4()
    author_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)
        add_user(
            db,
            user_id=author_id,
            organization_id=organization_id,
        )
        add_user(
            db,
            user_id=reviewer_id,
            organization_id=organization_id,
        )
        db.flush()

        service = ApprovalService(db)

        proposal = service.create(
            organization_id=organization_id,
            user_id=author_id,
            data=proposal_data(),
        )

        result = service.reject(
            organization_id=organization_id,
            proposal_id=proposal.id,
            user_id=reviewer_id,
            comment="Odrzucono.",
        )

        assert result.status == ApprovalStatus.REJECTED.value
        assert result.decided_by_user_id == reviewer_id

        db.rollback()


def test_author_cannot_approve_own_proposal() -> None:
    organization_id = uuid.uuid4()
    author_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)
        add_user(
            db,
            user_id=author_id,
            organization_id=organization_id,
        )
        db.flush()

        service = ApprovalService(db)

        proposal = service.create(
            organization_id=organization_id,
            user_id=author_id,
            data=proposal_data(),
        )

        with pytest.raises(ApprovalSeparationOfDutiesError):
            service.approve(
                organization_id=organization_id,
                proposal_id=proposal.id,
                user_id=author_id,
            )

        db.rollback()


def test_author_cannot_reject_own_proposal() -> None:
    organization_id = uuid.uuid4()
    author_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)
        add_user(
            db,
            user_id=author_id,
            organization_id=organization_id,
        )
        db.flush()

        service = ApprovalService(db)

        proposal = service.create(
            organization_id=organization_id,
            user_id=author_id,
            data=proposal_data(),
        )

        with pytest.raises(ApprovalSeparationOfDutiesError):
            service.reject(
                organization_id=organization_id,
                proposal_id=proposal.id,
                user_id=author_id,
            )

        db.rollback()


def test_final_state_is_immutable() -> None:
    organization_id = uuid.uuid4()
    author_id = uuid.uuid4()
    approver_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)

        for user_id in (
            author_id,
            approver_id,
            reviewer_id,
        ):
            add_user(
                db,
                user_id=user_id,
                organization_id=organization_id,
            )

        db.flush()

        service = ApprovalService(db)

        proposal = service.create(
            organization_id=organization_id,
            user_id=author_id,
            data=proposal_data(),
        )

        service.approve(
            organization_id=organization_id,
            proposal_id=proposal.id,
            user_id=approver_id,
        )

        with pytest.raises(ApprovalInvalidStateError):
            service.reject(
                organization_id=organization_id,
                proposal_id=proposal.id,
                user_id=reviewer_id,
            )

        db.rollback()


def test_cancel_pending_proposal() -> None:
    organization_id = uuid.uuid4()
    author_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)
        add_user(
            db,
            user_id=author_id,
            organization_id=organization_id,
        )
        db.flush()

        service = ApprovalService(db)

        proposal = service.create(
            organization_id=organization_id,
            user_id=author_id,
            data=proposal_data(),
        )

        result = service.cancel(
            organization_id=organization_id,
            proposal_id=proposal.id,
            comment="Anulowano.",
        )

        assert result.status == ApprovalStatus.CANCELLED.value
        assert result.decision_comment == "Anulowano."

        db.rollback()


def test_expired_proposal_cannot_be_approved() -> None:
    organization_id = uuid.uuid4()
    author_id = uuid.uuid4()
    approver_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)
        add_user(
            db,
            user_id=author_id,
            organization_id=organization_id,
        )
        add_user(
            db,
            user_id=approver_id,
            organization_id=organization_id,
        )
        db.flush()

        service = ApprovalService(db)

        proposal = service.create(
            organization_id=organization_id,
            user_id=author_id,
            data=proposal_data(
                expires_at=(
                    datetime.now(UTC)
                    - timedelta(minutes=1)
                ),
            ),
        )

        with pytest.raises(ApprovalInvalidStateError):
            service.approve(
                organization_id=organization_id,
                proposal_id=proposal.id,
                user_id=approver_id,
            )

        assert proposal.status == ApprovalStatus.EXPIRED.value

        db.rollback()


def test_modified_proposal_fails_fingerprint_validation() -> None:
    organization_id = uuid.uuid4()
    author_id = uuid.uuid4()
    approver_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)
        add_user(
            db,
            user_id=author_id,
            organization_id=organization_id,
        )
        add_user(
            db,
            user_id=approver_id,
            organization_id=organization_id,
        )
        db.flush()

        service = ApprovalService(db)

        proposal = service.create(
            organization_id=organization_id,
            user_id=author_id,
            data=proposal_data(),
        )

        proposal.payload = {
            "status": "completed",
            "priority": "high",
        }

        with pytest.raises(ApprovalFingerprintError):
            service.approve(
                organization_id=organization_id,
                proposal_id=proposal.id,
                user_id=approver_id,
            )

        db.rollback()