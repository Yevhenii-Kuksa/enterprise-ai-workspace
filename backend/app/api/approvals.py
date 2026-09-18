import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.approvals.dependencies import get_approval_service
from app.approvals.schemas import (
    ApprovalCancelRequest,
    ApprovalDecisionRequest,
    ApprovalProposalCreate,
    ApprovalStatus,
)
from app.approvals.schemas import (
    ApprovalProposal as ApprovalProposalSchema,
)
from app.approvals.service import (
    ApprovalFingerprintError,
    ApprovalInvalidStateError,
    ApprovalNotFoundError,
    ApprovalSeparationOfDutiesError,
    ApprovalService,
)
from app.audit.service import record_audit_event
from app.core.trace_context import TraceContext
from app.core.trace_dependencies import get_trace_context
from app.db.dependencies import get_db
from app.models.approval_proposal import ApprovalProposal
from app.security.current_user import CurrentUser
from app.security.permission_dependency import require_permission

router = APIRouter(
    prefix="/api/approvals",
    tags=["Approvals"],
)


def serialize_proposal(
    proposal: ApprovalProposal,
) -> ApprovalProposalSchema:
    return ApprovalProposalSchema.model_validate(
        proposal,
        from_attributes=True,
    )


def handle_approval_error(error: Exception) -> None:
    if isinstance(error, ApprovalNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    if isinstance(error, ApprovalSeparationOfDutiesError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    if isinstance(
        error,
        (
            ApprovalInvalidStateError,
            ApprovalFingerprintError,
        ),
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    raise error


@router.post(
    "",
    response_model=ApprovalProposalSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_approval(
    data: ApprovalProposalCreate,
    current_user: Annotated[
        CurrentUser,
        Depends(require_permission("approval.create")),
    ],
    service: Annotated[
        ApprovalService,
        Depends(get_approval_service),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    trace_context: Annotated[
        TraceContext,
        Depends(get_trace_context),
    ],
) -> ApprovalProposalSchema:
    proposal = service.create(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        data=data,
    )

    record_audit_event(
        db,
        current_user=current_user,
        trace_context=trace_context,
        event_type="approval_created",
        resource_type="approval_proposal",
        resource_id=str(proposal.id),
        metadata={
            "action_type": proposal.action_type,
            "target_resource_type": proposal.resource_type,
            "target_resource_id": proposal.resource_id,
            "status": proposal.status,
        },
    )

    db.commit()
    db.refresh(proposal)

    return serialize_proposal(proposal)


@router.get(
    "",
    response_model=list[ApprovalProposalSchema],
)
def list_approvals(
    current_user: Annotated[
        CurrentUser,
        Depends(require_permission("approval.read")),
    ],
    service: Annotated[
        ApprovalService,
        Depends(get_approval_service),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    approval_status: ApprovalStatus | None = None,
) -> list[ApprovalProposalSchema]:
    proposals = service.list(
        organization_id=current_user.organization_id,
        status=approval_status,
    )

    db.commit()

    return [
        serialize_proposal(proposal)
        for proposal in proposals
    ]


@router.get(
    "/{proposal_id}",
    response_model=ApprovalProposalSchema,
)
def get_approval(
    proposal_id: uuid.UUID,
    current_user: Annotated[
        CurrentUser,
        Depends(require_permission("approval.read")),
    ],
    service: Annotated[
        ApprovalService,
        Depends(get_approval_service),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> ApprovalProposalSchema:
    try:
        proposal = service.get(
            organization_id=current_user.organization_id,
            proposal_id=proposal_id,
        )
    except Exception as error:
        handle_approval_error(error)
        raise

    db.commit()

    return serialize_proposal(proposal)


@router.post(
    "/{proposal_id}/approve",
    response_model=ApprovalProposalSchema,
)
def approve_approval(
    proposal_id: uuid.UUID,
    data: ApprovalDecisionRequest,
    current_user: Annotated[
        CurrentUser,
        Depends(require_permission("approval.decide")),
    ],
    service: Annotated[
        ApprovalService,
        Depends(get_approval_service),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    trace_context: Annotated[
        TraceContext,
        Depends(get_trace_context),
    ],
) -> ApprovalProposalSchema:
    try:
        proposal = service.approve(
            organization_id=current_user.organization_id,
            proposal_id=proposal_id,
            user_id=current_user.id,
            comment=data.comment,
        )
    except Exception as error:
        handle_approval_error(error)
        raise

    record_audit_event(
        db,
        current_user=current_user,
        trace_context=trace_context,
        event_type="approval_approved",
        resource_type="approval_proposal",
        resource_id=str(proposal.id),
        metadata={
            "action_type": proposal.action_type,
            "target_resource_type": proposal.resource_type,
            "target_resource_id": proposal.resource_id,
            "status": proposal.status,
        },
    )

    db.commit()
    db.refresh(proposal)

    return serialize_proposal(proposal)


@router.post(
    "/{proposal_id}/reject",
    response_model=ApprovalProposalSchema,
)
def reject_approval(
    proposal_id: uuid.UUID,
    data: ApprovalDecisionRequest,
    current_user: Annotated[
        CurrentUser,
        Depends(require_permission("approval.decide")),
    ],
    service: Annotated[
        ApprovalService,
        Depends(get_approval_service),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    trace_context: Annotated[
        TraceContext,
        Depends(get_trace_context),
    ],
) -> ApprovalProposalSchema:
    try:
        proposal = service.reject(
            organization_id=current_user.organization_id,
            proposal_id=proposal_id,
            user_id=current_user.id,
            comment=data.comment,
        )
    except Exception as error:
        handle_approval_error(error)
        raise

    record_audit_event(
        db,
        current_user=current_user,
        trace_context=trace_context,
        event_type="approval_rejected",
        resource_type="approval_proposal",
        resource_id=str(proposal.id),
        metadata={
            "action_type": proposal.action_type,
            "target_resource_type": proposal.resource_type,
            "target_resource_id": proposal.resource_id,
            "status": proposal.status,
        },
    )

    db.commit()
    db.refresh(proposal)

    return serialize_proposal(proposal)


@router.post(
    "/{proposal_id}/cancel",
    response_model=ApprovalProposalSchema,
)
def cancel_approval(
    proposal_id: uuid.UUID,
    data: ApprovalCancelRequest,
    current_user: Annotated[
        CurrentUser,
        Depends(require_permission("approval.cancel")),
    ],
    service: Annotated[
        ApprovalService,
        Depends(get_approval_service),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    trace_context: Annotated[
        TraceContext,
        Depends(get_trace_context),
    ],
) -> ApprovalProposalSchema:
    try:
        proposal = service.cancel(
            organization_id=current_user.organization_id,
            proposal_id=proposal_id,
            comment=data.comment,
        )
    except Exception as error:
        handle_approval_error(error)
        raise

    record_audit_event(
        db,
        current_user=current_user,
        trace_context=trace_context,
        event_type="approval_cancelled",
        resource_type="approval_proposal",
        resource_id=str(proposal.id),
        metadata={
            "action_type": proposal.action_type,
            "target_resource_type": proposal.resource_type,
            "target_resource_id": proposal.resource_id,
            "status": proposal.status,
        },
    )

    db.commit()
    db.refresh(proposal)

    return serialize_proposal(proposal)