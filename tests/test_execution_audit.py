import uuid
from unittest.mock import MagicMock

from app.core.trace_context import TraceContext
from app.execution.audit import record_execution_audit_event
from app.security.current_user import CurrentUser


def test_execution_audit_event_uses_execution_as_action_id() -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    execution_id = uuid.uuid4()
    proposal_id = uuid.uuid4()

    current_user = CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={"action.execute"},
    )

    trace_context = TraceContext.create()

    session = MagicMock()

    event = record_execution_audit_event(
        session,
        current_user=current_user,
        trace_context=trace_context,
        execution_id=execution_id,
        proposal_id=proposal_id,
        action_type="order.update",
        status="succeeded",
        event_type="action_execution_succeeded",
    )

    assert event.organization_id == organization_id
    assert event.user_id == user_id

    assert event.trace_id == trace_context.trace_id
    assert event.request_id == trace_context.request_id
    assert event.action_id == execution_id

    assert event.event_type == "action_execution_succeeded"
    assert event.resource_type == "action_execution"
    assert event.resource_id == str(execution_id)

    assert event.metadata_json == {
        "execution_id": str(execution_id),
        "proposal_id": str(proposal_id),
        "action_type": "order.update",
        "status": "succeeded",
    }

    session.add.assert_called_once_with(event)