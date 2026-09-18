import uuid
from datetime import UTC, datetime

from app.execution.dependencies import execution_permission_dependency
from app.execution.schemas import ActionExecutionResponse, ExecutionStatus
from app.execution.service import (
    ExecutionError,
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
