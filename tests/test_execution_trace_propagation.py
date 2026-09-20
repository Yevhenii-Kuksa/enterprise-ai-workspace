import uuid
from datetime import UTC, datetime

from app.execution.dependencies import execution_permission_dependency
from app.execution.schemas import ActionExecutionResponse, ExecutionStatus
from app.execution.service_dependency import get_execution_service
from app.main import app
from app.security.current_user import CurrentUser
from fastapi.testclient import TestClient


def test_execute_endpoint_propagates_http_trace_context() -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    proposal_id = uuid.uuid4()
    execution_id = uuid.uuid4()
    trace_id = uuid.uuid4()
    now = datetime.now(UTC)

    current_user = CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={"action.execute"},
    )

    captured_trace_context: dict[str, object] = {}

    class FakeExecutionService:
        def execute_approved_proposal(
            self,
            **kwargs: object,
        ) -> ActionExecutionResponse:
            captured_trace_context["value"] = kwargs[
                "trace_context"
            ]

            trace_context = kwargs["trace_context"]

            return ActionExecutionResponse(
                id=execution_id,
                organization_id=organization_id,
                proposal_id=proposal_id,
                requested_by_user_id=user_id,
                action_type="order.update",
                status=ExecutionStatus.SUCCEEDED,
                idempotency_key="a" * 64,
                proposal_fingerprint="b" * 64,
                snapshot={
                    "action_type": "order.update",
                },
                attempt_count=1,
                max_attempts=3,
                result={"ok": True},
                error_code=None,
                error_message=None,
                trace_id=trace_context.trace_id,
                request_id=trace_context.request_id,
                created_at=now,
                started_at=now,
                finished_at=now,
                updated_at=now,
            )

    def override_execution_user() -> CurrentUser:
        return current_user

    def override_execution_service() -> FakeExecutionService:
        return FakeExecutionService()

    app.dependency_overrides[
        execution_permission_dependency
    ] = override_execution_user

    app.dependency_overrides[
        get_execution_service
    ] = override_execution_service

    try:
        client = TestClient(app)

        response = client.post(
            f"/executions/approvals/{proposal_id}/execute",
            headers={
                "X-Trace-ID": str(trace_id),
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    trace_context = captured_trace_context["value"]

    assert trace_context.trace_id == trace_id
    assert (
        str(trace_context.request_id)
        == response.headers["X-Request-ID"]
    )

    body = response.json()

    assert body["trace_id"] == str(trace_id)
    assert (
        body["request_id"]
        == response.headers["X-Request-ID"]
    )