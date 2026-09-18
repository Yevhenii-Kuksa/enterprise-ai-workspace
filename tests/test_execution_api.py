import uuid
from datetime import UTC, datetime

from app.execution.dependencies import execution_permission_dependency
from app.execution.schemas import ActionExecutionResponse, ExecutionStatus
from app.execution.service import (
    ExecutionActionDisabledError,
    ExecutionActionNotAllowedError,
    ExecutionError,
    ExecutionFingerprintError,
    ExecutionInvalidApprovalStateError,
)
from app.execution.service_dependency import get_execution_service
from app.main import app
from app.security.current_user import CurrentUser
from fastapi.testclient import TestClient

client = TestClient(app)


def test_execute_endpoint_requires_action_execute_permission() -> None:
    proposal_id = uuid.uuid4()

    response = client.post(
        f"/executions/approvals/{proposal_id}/execute"
    )

    assert response.status_code in {401, 403}


def test_execute_endpoint_returns_execution() -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    proposal_id = uuid.uuid4()
    execution_id = uuid.uuid4()
    now = datetime.now(UTC)

    current_user = CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={"action.execute"},
    )

    expected = ActionExecutionResponse(
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
        trace_id=uuid.uuid4(),
        request_id=uuid.uuid4(),
        created_at=now,
        started_at=now,
        finished_at=now,
        updated_at=now,
    )

    class FakeExecutionService:
        def execute_approved_proposal(
            self,
            **kwargs: object,
        ) -> ActionExecutionResponse:
            return expected

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
        response = client.post(
            f"/executions/approvals/{proposal_id}/execute"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == str(execution_id)
    assert body["proposal_id"] == str(proposal_id)
    assert body["status"] == "succeeded"
    assert body["action_type"] == "order.update"
    assert body["result"] == {"ok": True}

def test_get_execution_endpoint_returns_execution() -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    execution_id = uuid.uuid4()
    proposal_id = uuid.uuid4()
    now = datetime.now(UTC)

    current_user = CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={"action.execute"},
    )

    expected = ActionExecutionResponse(
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
        trace_id=uuid.uuid4(),
        request_id=uuid.uuid4(),
        created_at=now,
        started_at=now,
        finished_at=now,
        updated_at=now,
    )

    class FakeExecutionService:
        def get_execution(
            self,
            *,
            organization_id: uuid.UUID,
            execution_id: uuid.UUID,
        ) -> ActionExecutionResponse:
            assert organization_id == current_user.organization_id
            assert execution_id == expected.id
            return expected

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
        response = client.get(
            f"/executions/{execution_id}"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == str(execution_id)
    assert body["organization_id"] == str(organization_id)
    assert body["proposal_id"] == str(proposal_id)
    assert body["status"] == "succeeded"

def test_list_executions_endpoint_returns_executions() -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    proposal_id = uuid.uuid4()
    execution_id = uuid.uuid4()
    now = datetime.now(UTC)

    current_user = CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={"action.execute"},
    )

    expected = ActionExecutionResponse(
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
        trace_id=uuid.uuid4(),
        request_id=uuid.uuid4(),
        created_at=now,
        started_at=now,
        finished_at=now,
        updated_at=now,
    )

    class FakeExecutionService:
        def list_executions(
            self,
            *,
            organization_id: uuid.UUID,
            limit: int,
            offset: int,
        ) -> list[ActionExecutionResponse]:
            assert organization_id == current_user.organization_id
            assert limit == 100
            assert offset == 0

            return [expected]

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
        response = client.get(
            "/executions"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["id"] == str(execution_id)
    assert body[0]["organization_id"] == str(organization_id)
    assert body[0]["status"] == "succeeded"

def test_list_executions_endpoint_passes_pagination() -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    current_user = CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={"action.execute"},
    )

    class FakeExecutionService:
        def list_executions(
            self,
            *,
            organization_id: uuid.UUID,
            limit: int,
            offset: int,
        ) -> list[ActionExecutionResponse]:
            assert organization_id == current_user.organization_id
            assert limit == 25
            assert offset == 50

            return []

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
        response = client.get(
            "/executions?limit=25&offset=50"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == []

def test_list_executions_endpoint_rejects_invalid_limit() -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    current_user = CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={"action.execute"},
    )

    def override_execution_user() -> CurrentUser:
        return current_user

    app.dependency_overrides[
        execution_permission_dependency
    ] = override_execution_user

    try:
        response = client.get(
            "/executions?limit=101"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422

def test_get_execution_endpoint_returns_404_when_missing() -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    execution_id = uuid.uuid4()

    current_user = CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={"action.execute"},
    )

    class FakeExecutionService:
        def get_execution(
            self,
            *,
            organization_id: uuid.UUID,
            execution_id: uuid.UUID,
        ) -> ActionExecutionResponse:
            raise ExecutionError(
                "Execution not found."
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
        response = client.get(
            f"/executions/{execution_id}"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Execution not found."
    }

def test_execute_endpoint_returns_409_for_unapproved_proposal() -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    proposal_id = uuid.uuid4()

    current_user = CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={"action.execute"},
    )

    class FakeExecutionService:
        def execute_approved_proposal(
            self,
            **kwargs: object,
        ) -> ActionExecutionResponse:
            raise ExecutionInvalidApprovalStateError(
                "Only approved proposals can be executed."
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
        response = client.post(
            f"/executions/approvals/{proposal_id}/execute"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Proposal is not approved for execution."
    }


def test_execute_endpoint_returns_409_for_fingerprint_mismatch() -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    proposal_id = uuid.uuid4()

    current_user = CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={"action.execute"},
    )

    class FakeExecutionService:
        def execute_approved_proposal(
            self,
            **kwargs: object,
        ) -> ActionExecutionResponse:
            raise ExecutionFingerprintError(
                "Approval proposal fingerprint mismatch."
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
        response = client.post(
            f"/executions/approvals/{proposal_id}/execute"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Proposal integrity verification failed."
    }


def test_execute_endpoint_returns_403_for_disallowed_action() -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    proposal_id = uuid.uuid4()

    current_user = CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={"action.execute"},
    )

    class FakeExecutionService:
        def execute_approved_proposal(
            self,
            **kwargs: object,
        ) -> ActionExecutionResponse:
            raise ExecutionActionNotAllowedError(
                "Proposal action is not allowlisted."
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
        response = client.post(
            f"/executions/approvals/{proposal_id}/execute"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Action is not allowed for execution."
    }


def test_execute_endpoint_returns_403_for_disabled_action() -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    proposal_id = uuid.uuid4()

    current_user = CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={"action.execute"},
    )

    class FakeExecutionService:
        def execute_approved_proposal(
            self,
            **kwargs: object,
        ) -> ActionExecutionResponse:
            raise ExecutionActionDisabledError(
                "Proposal action is disabled."
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
        response = client.post(
            f"/executions/approvals/{proposal_id}/execute"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Action is disabled."
    }


def _run_execution_error_case(
    *,
    error: Exception,
    expected_status: int,
    expected_detail: str,
) -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    proposal_id = uuid.uuid4()

    current_user = CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={"action.execute"},
    )

    class FakeExecutionService:
        def execute_approved_proposal(
            self,
            **kwargs: object,
        ) -> ActionExecutionResponse:
            raise error

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
        response = client.post(
            f"/executions/approvals/{proposal_id}/execute"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == expected_status
    assert response.json() == {
        "detail": expected_detail
    }


def test_execute_endpoint_returns_404_when_proposal_missing() -> None:
    from app.approvals.service import ApprovalNotFoundError

    _run_execution_error_case(
        error=ApprovalNotFoundError(
            "Approval proposal not found."
        ),
        expected_status=404,
        expected_detail="Approval proposal not found.",
    )


def test_execute_endpoint_returns_409_for_expired_proposal() -> None:
    from app.execution.service import ExecutionApprovalExpiredError

    _run_execution_error_case(
        error=ExecutionApprovalExpiredError(
            "Approved proposal has expired."
        ),
        expected_status=409,
        expected_detail="Approval proposal has expired.",
    )


def test_execute_endpoint_returns_403_for_permission_denied() -> None:
    from app.execution.service import ExecutionPermissionError

    _run_execution_error_case(
        error=ExecutionPermissionError(
            "Execution permission denied."
        ),
        expected_status=403,
        expected_detail="Execution permission denied.",
    )


def test_execute_endpoint_returns_403_for_tenant_mismatch() -> None:
    from app.execution.service import ExecutionTenantError

    _run_execution_error_case(
        error=ExecutionTenantError(
            "Execution organization mismatch."
        ),
        expected_status=403,
        expected_detail="Execution organization mismatch.",
    )


def test_execute_endpoint_returns_409_for_invalid_execution_state() -> None:
    from app.execution.service import ExecutionInvalidStateError

    _run_execution_error_case(
        error=ExecutionInvalidStateError(
            "Execution has an unsupported state."
        ),
        expected_status=409,
        expected_detail="Execution is in an invalid state.",
    )


def test_execute_endpoint_returns_503_when_executor_unavailable() -> None:
    from app.execution.service import ExecutionExecutorNotAvailableError

    _run_execution_error_case(
        error=ExecutionExecutorNotAvailableError(
            "Action executor is not registered."
        ),
        expected_status=503,
        expected_detail="Execution service is temporarily unavailable.",
    )
