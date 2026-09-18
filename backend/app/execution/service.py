import uuid
from datetime import UTC, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.approvals.fingerprint import (
    verify_proposal_fingerprint,
)
from app.approvals.schemas import (
    ApprovalProposalSnapshot,
    ApprovalStatus,
)
from app.approvals.service import ApprovalService
from app.core.trace_context import TraceContext
from app.execution.audit import record_execution_audit_event
from app.execution.executor import (
    ActionExecutor,
    ExecutionContext,
    ExecutorNotRegisteredError,
    ExecutorRegistry,
)
from app.execution.idempotency import (
    calculate_execution_idempotency_key,
)
from app.execution.registry import (
    ActionNotRegisteredError,
    ActionRegistry,
)
from app.execution.schemas import (
    ExecutionResult,
    ExecutionStatus,
)
from app.models.action_execution import ActionExecution
from app.models.approval_proposal import ApprovalProposal
from app.security.current_user import CurrentUser


class ExecutionError(Exception):
    pass


class ExecutionInvalidApprovalStateError(ExecutionError):
    pass


class ExecutionApprovalExpiredError(ExecutionError):
    pass


class ExecutionActionNotAllowedError(ExecutionError):
    pass


class ExecutionActionDisabledError(ExecutionError):
    pass


class ExecutionPermissionError(ExecutionError):
    pass


class ExecutionFingerprintError(ExecutionError):
    pass


class ExecutionTenantError(ExecutionError):
    pass


class ExecutionExecutorNotAvailableError(ExecutionError):
    pass


class ExecutionInvalidStateError(ExecutionError):
    pass


class ExecutionService:
    def __init__(
        self,
        db: Session,
        registry: ActionRegistry,
        executors: ExecutorRegistry | None = None,
    ) -> None:
        self.db = db
        self.registry = registry
        self.executors = executors or ExecutorRegistry()

    def request_execution(
        self,
        *,
        organization_id: uuid.UUID,
        proposal_id: uuid.UUID,
        current_user: CurrentUser,
        trace_context: TraceContext,
    ) -> ActionExecution:
        if current_user.organization_id != organization_id:
            raise ExecutionTenantError(
                "Execution organization mismatch."
            )

        proposal = ApprovalService(self.db).get(
            organization_id=organization_id,
            proposal_id=proposal_id,
        )

        self._require_approved(proposal)
        self._require_not_expired(proposal)

        try:
            definition = self.registry.get(
                proposal.action_type
            )
        except ActionNotRegisteredError as exc:
            raise ExecutionActionNotAllowedError(
                "Proposal action is not allowlisted."
            ) from exc

        if not definition.enabled:
            raise ExecutionActionDisabledError(
                "Proposal action is disabled."
            )

        if (
            definition.required_permission
            not in current_user.permissions
        ):
            raise ExecutionPermissionError(
                "Execution permission denied."
            )

        current_snapshot = self._build_current_snapshot(
            proposal
        )

        serialized_snapshot = current_snapshot.model_dump(
            mode="json"
        )

        if proposal.snapshot != serialized_snapshot:
            raise ExecutionFingerprintError(
                "Approval snapshot mismatch."
            )

        if not verify_proposal_fingerprint(
            current_snapshot,
            proposal.fingerprint,
        ):
            raise ExecutionFingerprintError(
                "Approval proposal fingerprint mismatch."
            )

        idempotency_key = (
            calculate_execution_idempotency_key(
                organization_id=organization_id,
                proposal_id=proposal.id,
                proposal_fingerprint=proposal.fingerprint,
                action_type=proposal.action_type,
            )
        )

        existing = self._find_existing_execution(
            organization_id=organization_id,
            proposal_id=proposal.id,
            idempotency_key=idempotency_key,
        )

        if existing is not None:
            return existing

        execution = ActionExecution(
            id=uuid.uuid4(),
            organization_id=organization_id,
            proposal_id=proposal.id,
            requested_by_user_id=current_user.id,
            action_type=proposal.action_type,
            status=ExecutionStatus.PENDING.value,
            idempotency_key=idempotency_key,
            proposal_fingerprint=proposal.fingerprint,
            snapshot=serialized_snapshot,
            attempt_count=0,
            max_attempts=definition.max_attempts,
            trace_id=trace_context.trace_id,
            request_id=trace_context.request_id,
        )

        self.db.add(execution)
        self.db.flush()

        return execution

    def execute_approved_proposal(
        self,
        *,
        organization_id: uuid.UUID,
        proposal_id: uuid.UUID,
        current_user: CurrentUser,
        trace_context: TraceContext,
    ) -> ActionExecution:
        execution = self.request_execution(
            organization_id=organization_id,
            proposal_id=proposal_id,
            current_user=current_user,
            trace_context=trace_context,
        )

        if execution.status in {
            ExecutionStatus.SUCCEEDED.value,
            ExecutionStatus.FAILED.value,
            ExecutionStatus.RUNNING.value,
        }:
            return execution

        if execution.status != ExecutionStatus.PENDING.value:
            raise ExecutionInvalidStateError(
                "Execution has an unsupported state."
            )

        proposal = ApprovalService(self.db).get(
            organization_id=organization_id,
            proposal_id=proposal_id,
        )

        definition = self.registry.get(
            proposal.action_type
        )

        try:
            executor = self.executors.get(
                definition.executor_name
            )
        except ExecutorNotRegisteredError as exc:
            raise ExecutionExecutorNotAvailableError(
                "Action executor is not registered."
            ) from exc

        execution_trace_context = TraceContext.create(
            trace_id=trace_context.trace_id,
            request_id=trace_context.request_id,
            action_id=execution.id,
        )

        execution_context = ExecutionContext(
            action_id=execution.id,
            organization_id=organization_id,
            proposal_id=proposal.id,
            requested_by_user_id=current_user.id,
            action_type=proposal.action_type,
            resource_type=proposal.resource_type,
            resource_id=proposal.resource_id,
            payload=proposal.payload,
            trace_context=execution_trace_context,
        )

        return self._run_execution(
            execution=execution,
            executor=executor,
            context=execution_context,
            current_user=current_user,
        )

    def list_executions(
        self,
        *,
        organization_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ActionExecution]:
        statement = (
            select(ActionExecution)
            .where(
                ActionExecution.organization_id
                == organization_id
            )
            .order_by(ActionExecution.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_execution(
        self,
        *,
        organization_id: uuid.UUID,
        execution_id: uuid.UUID,
    ) -> ActionExecution:
        statement = select(ActionExecution).where(
            ActionExecution.id == execution_id,
            ActionExecution.organization_id == organization_id,
        )

        execution = self.db.scalar(statement)

        if execution is None:
            raise ExecutionError(
                "Execution not found."
            )

        return execution

    def _run_execution(
        self,
        *,
        execution: ActionExecution,
        executor: ActionExecutor,
        context: ExecutionContext,
        current_user: CurrentUser,
    ) -> ActionExecution:
        if execution.started_at is None:
            execution.started_at = datetime.now(UTC)

        while execution.attempt_count < execution.max_attempts:
            execution.status = ExecutionStatus.RUNNING.value
            execution.attempt_count += 1
            self.db.flush()

            result = self._execute_once(
                executor=executor,
                context=context,
            )

            if result.succeeded:
                execution.status = ExecutionStatus.SUCCEEDED.value
                execution.result = result.output
                execution.error_code = None
                execution.error_message = None
                execution.finished_at = datetime.now(UTC)

                record_execution_audit_event(
                    self.db,
                    current_user=current_user,
                    trace_context=context.trace_context,
                    execution_id=execution.id,
                    proposal_id=execution.proposal_id,
                    action_type=execution.action_type,
                    status=execution.status,
                    event_type="action_execution_succeeded",
                )

                self.db.flush()
                return execution

            execution.result = result.output
            execution.error_code = result.error_code
            execution.error_message = result.error_message

            can_retry = (
                result.retryable
                and execution.attempt_count
                < execution.max_attempts
            )

            if can_retry:
                continue

            execution.status = ExecutionStatus.FAILED.value
            execution.finished_at = datetime.now(UTC)

            record_execution_audit_event(
                self.db,
                current_user=current_user,
                trace_context=context.trace_context,
                execution_id=execution.id,
                proposal_id=execution.proposal_id,
                action_type=execution.action_type,
                status=execution.status,
                event_type="action_execution_failed",
            )

            self.db.flush()
            return execution

        execution.status = ExecutionStatus.FAILED.value
        execution.finished_at = datetime.now(UTC)

        record_execution_audit_event(
            self.db,
            current_user=current_user,
            trace_context=context.trace_context,
            execution_id=execution.id,
            proposal_id=execution.proposal_id,
            action_type=execution.action_type,
            status=execution.status,
            event_type="action_execution_failed",
        )

        self.db.flush()

        return execution

    @staticmethod
    def _execute_once(
        *,
        executor: ActionExecutor,
        context: ExecutionContext,
    ) -> ExecutionResult:
        try:
            result = executor.execute(
                context=context,
            )
        except Exception as exc:
            return ExecutionResult(
                succeeded=False,
                retryable=False,
                error_code="executor_exception",
                error_message=str(exc)[:2000],
            )

        if not isinstance(result, ExecutionResult):
            return ExecutionResult(
                succeeded=False,
                retryable=False,
                error_code="invalid_executor_result",
                error_message=(
                    "Executor returned an invalid result."
                ),
            )

        return result

    def _find_existing_execution(
        self,
        *,
        organization_id: uuid.UUID,
        proposal_id: uuid.UUID,
        idempotency_key: str,
    ) -> ActionExecution | None:
        statement = select(ActionExecution).where(
            ActionExecution.organization_id
            == organization_id,
            or_(
                ActionExecution.proposal_id == proposal_id,
                ActionExecution.idempotency_key
                == idempotency_key,
            ),
        )

        return self.db.scalar(statement)

    @staticmethod
    def _require_approved(
        proposal: ApprovalProposal,
    ) -> None:
        if proposal.status != ApprovalStatus.APPROVED.value:
            raise ExecutionInvalidApprovalStateError(
                "Only approved proposals can be executed."
            )

    @staticmethod
    def _require_not_expired(
        proposal: ApprovalProposal,
    ) -> None:
        if proposal.expires_at is None:
            return

        if proposal.expires_at <= datetime.now(UTC):
            raise ExecutionApprovalExpiredError(
                "Approved proposal has expired."
            )

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