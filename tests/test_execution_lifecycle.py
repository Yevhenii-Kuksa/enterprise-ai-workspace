import uuid

from app.approvals.schemas import ApprovalProposalCreate
from app.approvals.service import ApprovalService
from app.core.trace_context import TraceContext
from app.db.session import SessionLocal
from app.execution.executor import (
    ExecutionContext,
    ExecutorRegistry,
)
from app.execution.registry import ActionRegistry
from app.execution.schemas import (
    ActionDefinition,
    ExecutionResult,
    ExecutionStatus,
)
from app.execution.service import ExecutionService
from app.models.audit_event import AuditEvent
from app.models.organization import Organization
from app.models.user import User
from app.security.current_user import CurrentUser
from sqlalchemy import select

ACTION_TYPE = "order.update"
PERMISSION = "action.execute"
EXECUTOR_NAME = "test_executor"


class SequenceExecutor:
    def __init__(
        self,
        results: list[ExecutionResult | Exception],
    ) -> None:
        self.results = results
        self.calls = 0
        self.last_context: ExecutionContext | None = None

    def execute(
        self,
        *,
        context: ExecutionContext,
    ) -> ExecutionResult:
        self.calls += 1
        self.last_context = context

        result = self.results[self.calls - 1]

        if isinstance(result, Exception):
            raise result

        return result


def add_organization(
    db: object,
    organization_id: uuid.UUID,
) -> None:
    db.add(
        Organization(
            id=organization_id,
            code=f"EXEC-LIFE-{organization_id.hex[:8]}",
            name="Execution Lifecycle Test",
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
            full_name="Execution Lifecycle User",
        )
    )


def build_current_user(
    *,
    user_id: uuid.UUID,
    organization_id: uuid.UUID,
) -> CurrentUser:
    return CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={PERMISSION},
    )


def build_service(
    db: object,
    executor: SequenceExecutor,
    *,
    max_attempts: int = 3,
) -> ExecutionService:
    actions = ActionRegistry(
        [
            ActionDefinition(
                action_type=ACTION_TYPE,
                executor_name=EXECUTOR_NAME,
                required_permission=PERMISSION,
                max_attempts=max_attempts,
            )
        ]
    )

    executors = ExecutorRegistry()
    executors.register(
        EXECUTOR_NAME,
        executor,
    )

    return ExecutionService(
        db,
        actions,
        executors,
    )


def create_approved_proposal(
    db: object,
    *,
    organization_id: uuid.UUID,
    author_id: uuid.UUID,
    approver_id: uuid.UUID,
):
    service = ApprovalService(db)

    proposal = service.create(
        organization_id=organization_id,
        user_id=author_id,
        data=ApprovalProposalCreate(
            action_type=ACTION_TYPE,
            resource_type="order",
            resource_id="ORDER-001",
            payload={
                "status": "confirmed",
            },
            justification="Execution lifecycle test.",
        ),
    )

    service.approve(
        organization_id=organization_id,
        proposal_id=proposal.id,
        user_id=approver_id,
    )

    return proposal


def prepare_execution_test():
    organization_id = uuid.uuid4()
    author_id = uuid.uuid4()
    approver_id = uuid.uuid4()
    executor_id = uuid.uuid4()

    return (
        organization_id,
        author_id,
        approver_id,
        executor_id,
    )


def test_successful_execution() -> None:
    (
        organization_id,
        author_id,
        approver_id,
        executor_id,
    ) = prepare_execution_test()

    executor = SequenceExecutor(
        [
            ExecutionResult(
                succeeded=True,
                output={"ok": True},
            )
        ]
    )

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

        execution = build_service(
            db,
            executor,
        ).execute_approved_proposal(
            organization_id=organization_id,
            proposal_id=proposal.id,
            current_user=build_current_user(
                user_id=executor_id,
                organization_id=organization_id,
            ),
            trace_context=trace_context,
        )

        assert execution.status == ExecutionStatus.SUCCEEDED.value
        assert execution.attempt_count == 1
        assert execution.result == {"ok": True}
        assert execution.started_at is not None
        assert execution.finished_at is not None
        assert executor.calls == 1
        assert executor.last_context is not None
        assert executor.last_context.action_id == execution.id

        audit_event = db.scalar(
            select(AuditEvent).where(
                AuditEvent.action_id == execution.id,
                AuditEvent.event_type
                == "action_execution_succeeded",
            )
        )

        assert audit_event is not None
        assert audit_event.organization_id == organization_id
        assert audit_event.user_id == executor_id
        assert audit_event.trace_id == trace_context.trace_id
        assert audit_event.action_id == execution.id
        assert audit_event.resource_type == "action_execution"
        assert audit_event.resource_id == str(execution.id)

        db.rollback()


def test_retryable_failure_then_success() -> None:
    (
        organization_id,
        author_id,
        approver_id,
        executor_id,
    ) = prepare_execution_test()

    executor = SequenceExecutor(
        [
            ExecutionResult(
                succeeded=False,
                retryable=True,
                error_code="temporary_failure",
                error_message="Temporary error.",
            ),
            ExecutionResult(
                succeeded=True,
                output={"retry": "worked"},
            ),
        ]
    )

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

        execution = build_service(
            db,
            executor,
        ).execute_approved_proposal(
            organization_id=organization_id,
            proposal_id=proposal.id,
            current_user=build_current_user(
                user_id=executor_id,
                organization_id=organization_id,
            ),
            trace_context=TraceContext.create(),
        )

        assert execution.status == ExecutionStatus.SUCCEEDED.value
        assert execution.attempt_count == 2
        assert execution.result == {"retry": "worked"}
        assert execution.error_code is None
        assert execution.error_message is None
        assert executor.calls == 2

        db.rollback()


def test_retry_exhaustion_fails_execution() -> None:
    (
        organization_id,
        author_id,
        approver_id,
        executor_id,
    ) = prepare_execution_test()

    failure = ExecutionResult(
        succeeded=False,
        retryable=True,
        error_code="temporary_failure",
        error_message="Still unavailable.",
    )

    executor = SequenceExecutor(
        [
            failure,
            failure,
            failure,
        ]
    )

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

        execution = build_service(
            db,
            executor,
            max_attempts=3,
        ).execute_approved_proposal(
            organization_id=organization_id,
            proposal_id=proposal.id,
            current_user=build_current_user(
                user_id=executor_id,
                organization_id=organization_id,
            ),
            trace_context=TraceContext.create(),
        )

        assert execution.status == ExecutionStatus.FAILED.value
        assert execution.attempt_count == 3
        assert execution.error_code == "temporary_failure"
        assert execution.finished_at is not None
        assert executor.calls == 3

        db.rollback()


def test_non_retryable_failure_stops_immediately() -> None:
    (
        organization_id,
        author_id,
        approver_id,
        executor_id,
    ) = prepare_execution_test()

    executor = SequenceExecutor(
        [
            ExecutionResult(
                succeeded=False,
                retryable=False,
                error_code="validation_error",
                error_message="Invalid action payload.",
            )
        ]
    )

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

        execution = build_service(
            db,
            executor,
        ).execute_approved_proposal(
            organization_id=organization_id,
            proposal_id=proposal.id,
            current_user=build_current_user(
                user_id=executor_id,
                organization_id=organization_id,
            ),
            trace_context=TraceContext.create(),
        )

        assert execution.status == ExecutionStatus.FAILED.value
        assert execution.attempt_count == 1
        assert execution.error_code == "validation_error"
        assert executor.calls == 1

        db.rollback()


def test_executor_exception_becomes_controlled_failure() -> None:
    (
        organization_id,
        author_id,
        approver_id,
        executor_id,
    ) = prepare_execution_test()

    executor = SequenceExecutor(
        [
            RuntimeError("Executor crashed."),
        ]
    )

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

        execution = build_service(
            db,
            executor,
        ).execute_approved_proposal(
            organization_id=organization_id,
            proposal_id=proposal.id,
            current_user=build_current_user(
                user_id=executor_id,
                organization_id=organization_id,
            ),
            trace_context=TraceContext.create(),
        )

        assert execution.status == ExecutionStatus.FAILED.value
        assert execution.attempt_count == 1
        assert execution.error_code == "executor_exception"
        assert execution.error_message == "Executor crashed."
        assert executor.calls == 1

        audit_event = db.scalar(
            select(AuditEvent).where(
                AuditEvent.action_id == execution.id,
                AuditEvent.event_type
                == "action_execution_failed",
            )
        )

        assert audit_event is not None
        assert audit_event.organization_id == organization_id
        assert audit_event.user_id == executor_id
        assert audit_event.resource_type == "action_execution"
        assert audit_event.resource_id == str(execution.id)
        assert audit_event.action_id == execution.id

        db.rollback()


def test_successful_execution_is_not_replayed() -> None:
    (
        organization_id,
        author_id,
        approver_id,
        executor_id,
    ) = prepare_execution_test()

    executor = SequenceExecutor(
        [
            ExecutionResult(
                succeeded=True,
                output={"completed": True},
            )
        ]
    )

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

        service = build_service(
            db,
            executor,
        )

        user = build_current_user(
            user_id=executor_id,
            organization_id=organization_id,
        )

        first = service.execute_approved_proposal(
            organization_id=organization_id,
            proposal_id=proposal.id,
            current_user=user,
            trace_context=TraceContext.create(),
        )

        second = service.execute_approved_proposal(
            organization_id=organization_id,
            proposal_id=proposal.id,
            current_user=user,
            trace_context=TraceContext.create(),
        )

        assert second.id == first.id
        assert second.status == ExecutionStatus.SUCCEEDED.value
        assert executor.calls == 1

        db.rollback()