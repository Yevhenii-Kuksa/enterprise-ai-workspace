import uuid

import pytest
from app.approvals.schemas import ApprovalProposalCreate
from app.approvals.service import ApprovalService
from app.core.trace_context import TraceContext
from app.db.session import SessionLocal
from app.execution.registry import ActionRegistry
from app.execution.schemas import (
    ActionDefinition,
    ExecutionStatus,
)
from app.execution.service import (
    ExecutionActionDisabledError,
    ExecutionActionNotAllowedError,
    ExecutionError,
    ExecutionFingerprintError,
    ExecutionInvalidApprovalStateError,
    ExecutionPermissionError,
    ExecutionService,
)
from app.models.organization import Organization
from app.models.user import User
from app.security.current_user import CurrentUser

ACTION_TYPE = "order.update"
EXECUTION_PERMISSION = "action.execute"


def add_organization(
    db: object,
    organization_id: uuid.UUID,
) -> None:
    db.add(
        Organization(
            id=organization_id,
            code=f"EXEC-{organization_id.hex[:8]}",
            name="Execution Test Organization",
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
            full_name="Execution Test User",
        )
    )


def proposal_data(
    action_type: str = ACTION_TYPE,
) -> ApprovalProposalCreate:
    return ApprovalProposalCreate(
        action_type=action_type,
        resource_type="order",
        resource_id="ORDER-001",
        payload={
            "status": "confirmed",
        },
        justification="Execution test.",
    )


def registry(
    *,
    enabled: bool = True,
) -> ActionRegistry:
    return ActionRegistry(
        [
            ActionDefinition(
                action_type=ACTION_TYPE,
                executor_name="test_executor",
                required_permission=EXECUTION_PERMISSION,
                enabled=enabled,
                max_attempts=3,
            )
        ]
    )


def current_user(
    *,
    user_id: uuid.UUID,
    organization_id: uuid.UUID,
    permissions: set[str] | None = None,
) -> CurrentUser:
    return CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions=(
            permissions
            if permissions is not None
            else {EXECUTION_PERMISSION}
        ),
    )


def create_approved_proposal(
    db: object,
    *,
    organization_id: uuid.UUID,
    author_id: uuid.UUID,
    approver_id: uuid.UUID,
    action_type: str = ACTION_TYPE,
):
    service = ApprovalService(db)

    proposal = service.create(
        organization_id=organization_id,
        user_id=author_id,
        data=proposal_data(action_type),
    )

    service.approve(
        organization_id=organization_id,
        proposal_id=proposal.id,
        user_id=approver_id,
    )

    return proposal


def test_request_execution_for_approved_proposal() -> None:
    organization_id = uuid.uuid4()
    author_id = uuid.uuid4()
    approver_id = uuid.uuid4()
    executor_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)

        for user_id in (
            author_id,
            approver_id,
            executor_id,
        ):
            add_user(
                db,
                user_id=user_id,
                organization_id=organization_id,
            )

        db.flush()

        proposal = create_approved_proposal(
            db,
            organization_id=organization_id,
            author_id=author_id,
            approver_id=approver_id,
        )

        trace_context = TraceContext.create()

        execution = ExecutionService(
            db,
            registry(),
        ).request_execution(
            organization_id=organization_id,
            proposal_id=proposal.id,
            current_user=current_user(
                user_id=executor_id,
                organization_id=organization_id,
            ),
            trace_context=trace_context,
        )

        assert execution.proposal_id == proposal.id
        assert execution.action_type == ACTION_TYPE
        assert execution.status == ExecutionStatus.PENDING.value
        assert execution.attempt_count == 0
        assert execution.max_attempts == 3
        assert len(execution.idempotency_key) == 64
        assert execution.trace_id == trace_context.trace_id
        assert execution.request_id == trace_context.request_id

        db.rollback()


def test_pending_proposal_cannot_execute() -> None:
    organization_id = uuid.uuid4()
    author_id = uuid.uuid4()
    executor_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)

        for user_id in (
            author_id,
            executor_id,
        ):
            add_user(
                db,
                user_id=user_id,
                organization_id=organization_id,
            )

        db.flush()

        proposal = ApprovalService(db).create(
            organization_id=organization_id,
            user_id=author_id,
            data=proposal_data(),
        )

        with pytest.raises(
            ExecutionInvalidApprovalStateError
        ):
            ExecutionService(
                db,
                registry(),
            ).request_execution(
                organization_id=organization_id,
                proposal_id=proposal.id,
                current_user=current_user(
                    user_id=executor_id,
                    organization_id=organization_id,
                ),
                trace_context=TraceContext.create(),
            )

        db.rollback()


def test_unknown_action_is_blocked() -> None:
    organization_id = uuid.uuid4()
    author_id = uuid.uuid4()
    approver_id = uuid.uuid4()
    executor_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)

        for user_id in (
            author_id,
            approver_id,
            executor_id,
        ):
            add_user(
                db,
                user_id=user_id,
                organization_id=organization_id,
            )

        db.flush()

        proposal = create_approved_proposal(
            db,
            organization_id=organization_id,
            author_id=author_id,
            approver_id=approver_id,
            action_type="unknown.action",
        )

        with pytest.raises(
            ExecutionActionNotAllowedError
        ):
            ExecutionService(
                db,
                registry(),
            ).request_execution(
                organization_id=organization_id,
                proposal_id=proposal.id,
                current_user=current_user(
                    user_id=executor_id,
                    organization_id=organization_id,
                ),
                trace_context=TraceContext.create(),
            )

        db.rollback()


def test_disabled_action_is_blocked() -> None:
    organization_id = uuid.uuid4()
    author_id = uuid.uuid4()
    approver_id = uuid.uuid4()
    executor_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)

        for user_id in (
            author_id,
            approver_id,
            executor_id,
        ):
            add_user(
                db,
                user_id=user_id,
                organization_id=organization_id,
            )

        db.flush()

        proposal = create_approved_proposal(
            db,
            organization_id=organization_id,
            author_id=author_id,
            approver_id=approver_id,
        )

        with pytest.raises(
            ExecutionActionDisabledError
        ):
            ExecutionService(
                db,
                registry(enabled=False),
            ).request_execution(
                organization_id=organization_id,
                proposal_id=proposal.id,
                current_user=current_user(
                    user_id=executor_id,
                    organization_id=organization_id,
                ),
                trace_context=TraceContext.create(),
            )

        db.rollback()


def test_missing_action_permission_is_blocked() -> None:
    organization_id = uuid.uuid4()
    author_id = uuid.uuid4()
    approver_id = uuid.uuid4()
    executor_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)

        for user_id in (
            author_id,
            approver_id,
            executor_id,
        ):
            add_user(
                db,
                user_id=user_id,
                organization_id=organization_id,
            )

        db.flush()

        proposal = create_approved_proposal(
            db,
            organization_id=organization_id,
            author_id=author_id,
            approver_id=approver_id,
        )

        with pytest.raises(ExecutionPermissionError):
            ExecutionService(
                db,
                registry(),
            ).request_execution(
                organization_id=organization_id,
                proposal_id=proposal.id,
                current_user=current_user(
                    user_id=executor_id,
                    organization_id=organization_id,
                    permissions=set(),
                ),
                trace_context=TraceContext.create(),
            )

        db.rollback()


def test_modified_proposal_is_blocked() -> None:
    organization_id = uuid.uuid4()
    author_id = uuid.uuid4()
    approver_id = uuid.uuid4()
    executor_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)

        for user_id in (
            author_id,
            approver_id,
            executor_id,
        ):
            add_user(
                db,
                user_id=user_id,
                organization_id=organization_id,
            )

        db.flush()

        proposal = create_approved_proposal(
            db,
            organization_id=organization_id,
            author_id=author_id,
            approver_id=approver_id,
        )

        proposal.payload = {
            "status": "tampered",
        }
        db.flush()

        with pytest.raises(ExecutionFingerprintError):
            ExecutionService(
                db,
                registry(),
            ).request_execution(
                organization_id=organization_id,
                proposal_id=proposal.id,
                current_user=current_user(
                    user_id=executor_id,
                    organization_id=organization_id,
                ),
                trace_context=TraceContext.create(),
            )

        db.rollback()


def test_repeated_request_returns_same_execution() -> None:
    organization_id = uuid.uuid4()
    author_id = uuid.uuid4()
    approver_id = uuid.uuid4()
    executor_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)

        for user_id in (
            author_id,
            approver_id,
            executor_id,
        ):
            add_user(
                db,
                user_id=user_id,
                organization_id=organization_id,
            )

        db.flush()

        proposal = create_approved_proposal(
            db,
            organization_id=organization_id,
            author_id=author_id,
            approver_id=approver_id,
        )

        service = ExecutionService(
            db,
            registry(),
        )

        user = current_user(
            user_id=executor_id,
            organization_id=organization_id,
        )

        first = service.request_execution(
            organization_id=organization_id,
            proposal_id=proposal.id,
            current_user=user,
            trace_context=TraceContext.create(),
        )

        second = service.request_execution(
            organization_id=organization_id,
            proposal_id=proposal.id,
            current_user=user,
            trace_context=TraceContext.create(),
        )

        assert second.id == first.id
        assert second.idempotency_key == first.idempotency_key

        db.rollback()

def test_get_execution_returns_execution_for_same_organization() -> None:
    organization_id = uuid.uuid4()
    author_id = uuid.uuid4()
    approver_id = uuid.uuid4()
    executor_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)

        for user_id in (
            author_id,
            approver_id,
            executor_id,
        ):
            add_user(
                db,
                user_id=user_id,
                organization_id=organization_id,
            )

        db.flush()

        proposal = create_approved_proposal(
            db,
            organization_id=organization_id,
            author_id=author_id,
            approver_id=approver_id,
        )

        service = ExecutionService(
            db,
            registry(),
        )

        execution = service.request_execution(
            organization_id=organization_id,
            proposal_id=proposal.id,
            current_user=current_user(
                user_id=executor_id,
                organization_id=organization_id,
            ),
            trace_context=TraceContext.create(),
        )

        found = service.get_execution(
            organization_id=organization_id,
            execution_id=execution.id,
        )

        assert found.id == execution.id
        assert found.organization_id == organization_id

        db.rollback()

def test_get_execution_blocks_cross_tenant_access() -> None:
    organization_id = uuid.uuid4()
    other_organization_id = uuid.uuid4()
    author_id = uuid.uuid4()
    approver_id = uuid.uuid4()
    executor_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)
        add_organization(db, other_organization_id)

        for user_id in (
            author_id,
            approver_id,
            executor_id,
        ):
            add_user(
                db,
                user_id=user_id,
                organization_id=organization_id,
            )

        db.flush()

        proposal = create_approved_proposal(
            db,
            organization_id=organization_id,
            author_id=author_id,
            approver_id=approver_id,
        )

        service = ExecutionService(
            db,
            registry(),
        )

        execution = service.request_execution(
            organization_id=organization_id,
            proposal_id=proposal.id,
            current_user=current_user(
                user_id=executor_id,
                organization_id=organization_id,
            ),
            trace_context=TraceContext.create(),
        )

        with pytest.raises(ExecutionError):
            service.get_execution(
                organization_id=other_organization_id,
                execution_id=execution.id,
            )

        db.rollback()

def test_list_executions_returns_only_same_organization() -> None:
    organization_id = uuid.uuid4()
    other_organization_id = uuid.uuid4()

    author_id = uuid.uuid4()
    approver_id = uuid.uuid4()
    executor_id = uuid.uuid4()

    other_author_id = uuid.uuid4()
    other_approver_id = uuid.uuid4()
    other_executor_id = uuid.uuid4()

    with SessionLocal() as db:
        add_organization(db, organization_id)
        add_organization(db, other_organization_id)

        for user_id in (
            author_id,
            approver_id,
            executor_id,
        ):
            add_user(
                db,
                user_id=user_id,
                organization_id=organization_id,
            )

        for user_id in (
            other_author_id,
            other_approver_id,
            other_executor_id,
        ):
            add_user(
                db,
                user_id=user_id,
                organization_id=other_organization_id,
            )

        db.flush()

        proposal = create_approved_proposal(
            db,
            organization_id=organization_id,
            author_id=author_id,
            approver_id=approver_id,
        )

        other_proposal = create_approved_proposal(
            db,
            organization_id=other_organization_id,
            author_id=other_author_id,
            approver_id=other_approver_id,
        )

        service = ExecutionService(
            db,
            registry(),
        )

        execution = service.request_execution(
            organization_id=organization_id,
            proposal_id=proposal.id,
            current_user=current_user(
                user_id=executor_id,
                organization_id=organization_id,
            ),
            trace_context=TraceContext.create(),
        )

        service.request_execution(
            organization_id=other_organization_id,
            proposal_id=other_proposal.id,
            current_user=current_user(
                user_id=other_executor_id,
                organization_id=other_organization_id,
            ),
            trace_context=TraceContext.create(),
        )

        executions = service.list_executions(
            organization_id=organization_id,
        )

        assert len(executions) == 1
        assert executions[0].id == execution.id
        assert executions[0].organization_id == organization_id

        db.rollback()