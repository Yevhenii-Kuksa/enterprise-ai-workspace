import uuid

from sqlalchemy.orm import Session

from app.audit.service import record_audit_event
from app.core.trace_context import TraceContext
from app.models.audit_event import AuditEvent
from app.security.current_user import CurrentUser


def record_execution_audit_event(
    session: Session,
    *,
    current_user: CurrentUser,
    trace_context: TraceContext,
    execution_id: uuid.UUID,
    proposal_id: uuid.UUID,
    action_type: str,
    status: str,
    event_type: str,
) -> AuditEvent:
    action_trace_context = TraceContext.create(
        trace_id=trace_context.trace_id,
        request_id=trace_context.request_id,
        action_id=execution_id,
    )

    return record_audit_event(
        session,
        current_user=current_user,
        trace_context=action_trace_context,
        event_type=event_type,
        resource_type="action_execution",
        resource_id=str(execution_id),
        metadata={
            "execution_id": str(execution_id),
            "proposal_id": str(proposal_id),
            "action_type": action_type,
            "status": status,
        },
    )