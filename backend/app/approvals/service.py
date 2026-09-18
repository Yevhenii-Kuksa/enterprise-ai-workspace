import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.approvals.fingerprint import (
    calculate_proposal_fingerprint,
    verify_proposal_fingerprint,
)
from app.approvals.schemas import (
    ApprovalProposalCreate,
    ApprovalProposalSnapshot,
    ApprovalStatus,
)
from app.models.approval_proposal import ApprovalProposal


class ApprovalError(Exception):
    pass


class ApprovalNotFoundError(ApprovalError):
    pass


class ApprovalInvalidStateError(ApprovalError):
    pass


class ApprovalSeparationOfDutiesError(ApprovalError):
    pass


class ApprovalFingerprintError(ApprovalError):
    pass


class ApprovalService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        data: ApprovalProposalCreate,
    ) -> ApprovalProposal:
        snapshot = ApprovalProposalSnapshot(
            action_type=data.action_type,
            resource_type=data.resource_type,
            resource_id=data.resource_id,
            payload=data.payload,
            justification=data.justification,
        )

        proposal = ApprovalProposal(
            organization_id=organization_id,
            created_by_user_id=user_id,
            status=ApprovalStatus.PENDING.value,
            action_type=data.action_type,
            resource_type=data.resource_type,
            resource_id=data.resource_id,
            payload=data.payload,
            justification=data.justification,
            snapshot=snapshot.model_dump(mode="json"),
            fingerprint=calculate_proposal_fingerprint(snapshot),
            expires_at=data.expires_at,
        )

        self.db.add(proposal)
        self.db.flush()
        return proposal

    def get(
        self,
        *,
        organization_id: uuid.UUID,
        proposal_id: uuid.UUID,
    ) -> ApprovalProposal:
        statement = select(ApprovalProposal).where(
            ApprovalProposal.id == proposal_id,
            ApprovalProposal.organization_id == organization_id,
        )
        proposal = self.db.scalar(statement)
        if proposal is None:
            raise ApprovalNotFoundError(
                "Approval proposal not found."
            )

        self._expire_if_needed(proposal)
        return proposal

    def list(
        self,
        *,
        organization_id: uuid.UUID,
        status: ApprovalStatus | None = None,
    ) -> list[ApprovalProposal]:
        statement = select(ApprovalProposal).where(
            ApprovalProposal.organization_id == organization_id
        )

        if status is not None:
            statement = statement.where(
                ApprovalProposal.status == status.value
            )

        statement = statement.order_by(
            ApprovalProposal.created_at.desc()
        )

        proposals = list(
            self.db.scalars(statement).all()
        )

        for proposal in proposals:
            self._expire_if_needed(proposal)

        if status is not None:
            proposals = [
                proposal
                for proposal in proposals
                if proposal.status == status.value
            ]

        return proposals

    def count_by_status(
        self,
        *,
        organization_id: uuid.UUID,
        status: ApprovalStatus,
    ) -> int:
        statement = (
            select(func.count())
            .select_from(ApprovalProposal)
            .where(
                ApprovalProposal.organization_id
                == organization_id,
                ApprovalProposal.status == status.value,
            )
        )

        return int(
            self.db.scalar(statement) or 0
        )

    def approve(
        self,
        *,
        organization_id: uuid.UUID,
        proposal_id: uuid.UUID,
        user_id: uuid.UUID,
        comment: str | None = None,
    ) -> ApprovalProposal:
        proposal = self.get(
            organization_id=organization_id,
            proposal_id=proposal_id,
        )

        self._validate_decision(
            proposal=proposal,
            user_id=user_id,
        )

        proposal.status = ApprovalStatus.APPROVED.value
        proposal.decided_by_user_id = user_id
        proposal.decided_at = datetime.now(UTC)
        proposal.decision_comment = comment

        self.db.flush()
        return proposal

    def reject(
        self,
        *,
        organization_id: uuid.UUID,
        proposal_id: uuid.UUID,
        user_id: uuid.UUID,
        comment: str | None = None,
    ) -> ApprovalProposal:
        proposal = self.get(
            organization_id=organization_id,
            proposal_id=proposal_id,
        )

        self._validate_decision(
            proposal=proposal,
            user_id=user_id,
        )

        proposal.status = ApprovalStatus.REJECTED.value
        proposal.decided_by_user_id = user_id
        proposal.decided_at = datetime.now(UTC)
        proposal.decision_comment = comment

        self.db.flush()
        return proposal

    def cancel(
        self,
        *,
        organization_id: uuid.UUID,
        proposal_id: uuid.UUID,
        comment: str | None = None,
    ) -> ApprovalProposal:
        proposal = self.get(
            organization_id=organization_id,
            proposal_id=proposal_id,
        )

        self._require_pending(proposal)

        proposal.status = ApprovalStatus.CANCELLED.value
        proposal.decided_at = datetime.now(UTC)
        proposal.decision_comment = comment

        self.db.flush()
        return proposal

    def _validate_decision(
        self,
        *,
        proposal: ApprovalProposal,
        user_id: uuid.UUID,
    ) -> None:
        self._require_pending(proposal)

        if proposal.created_by_user_id == user_id:
            raise ApprovalSeparationOfDutiesError(
                "Proposal author cannot approve or reject "
                "their own proposal."
            )

        current_snapshot = self._build_current_snapshot(
            proposal
        )

        if not verify_proposal_fingerprint(
            current_snapshot,
            proposal.fingerprint,
        ):
            raise ApprovalFingerprintError(
                "Approval proposal fingerprint mismatch."
            )

    @staticmethod
    def _require_pending(
        proposal: ApprovalProposal,
    ) -> None:
        if proposal.status != ApprovalStatus.PENDING.value:
            raise ApprovalInvalidStateError(
                "Approval proposal is not pending."
            )

    def _expire_if_needed(
        self,
        proposal: ApprovalProposal,
    ) -> None:
        if proposal.status != ApprovalStatus.PENDING.value:
            return

        if proposal.expires_at is None:
            return

        if proposal.expires_at > datetime.now(UTC):
            return

        proposal.status = ApprovalStatus.EXPIRED.value
        self.db.flush()

    @staticmethod
    def _build_current_snapshot(
        proposal: ApprovalProposal,
    ) -> ApprovalProposalSnapshot:
        return ApprovalProposalSnapshot(
            action_type=proposal.action_type,
            resource_type=proposal.resource_type,
            resource_id=proposal.resource_id,
            payload=proposal.payload,
            justification=proposal.justification,
        )