import uuid

from app.core.trace_context import TraceContext
from app.core.trace_dependencies import get_trace_context
from app.db.dependencies import get_db
from app.models.audit_event import AuditEvent
from app.security.current_user import CurrentUser
from app.security.dependencies import get_current_user
from app.security.permission_dependency import require_permission
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

knowledge_read_dependency = require_permission("knowledge.read")
required_permission_dependency = Depends(knowledge_read_dependency)


class FakeDb:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.flushed = False
        self.committed = False

    def add(self, instance: object) -> None:
        self.added.append(instance)

    def flush(self) -> None:
        self.flushed = True

    def commit(self) -> None:
        self.committed = True


@app.get("/test-permission")
def protected_endpoint(
    current_user: CurrentUser = required_permission_dependency,
) -> dict[str, str]:
    return {"user_id": str(current_user.id)}


client = TestClient(app)


def test_permission_dependency_allows_required_permission() -> None:
    user_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    fake_db = FakeDb()

    trace_context = TraceContext.create()

    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={"knowledge.read"},
    )
    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_trace_context] = lambda: trace_context

    try:
        response = client.get("/test-permission")

        assert response.status_code == 200
        assert response.json() == {
            "user_id": str(user_id),
        }

        assert fake_db.added == []
        assert fake_db.flushed is False
        assert fake_db.committed is False
    finally:
        app.dependency_overrides.clear()


def test_permission_dependency_rejects_missing_permission() -> None:
    user_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    trace_id = uuid.uuid4()
    fake_db = FakeDb()

    trace_context = TraceContext.create(
        trace_id=trace_id,
    )

    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id=user_id,
        organization_id=organization_id,
        is_active=True,
        permissions={"audit.read"},
    )
    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_trace_context] = lambda: trace_context

    try:
        response = client.get("/test-permission")

        assert response.status_code == 403
        assert response.json() == {
            "detail": "Permission denied.",
        }

        assert fake_db.flushed is True
        assert fake_db.committed is True
        assert len(fake_db.added) == 1

        audit_event = fake_db.added[0]

        assert isinstance(audit_event, AuditEvent)

        assert audit_event.organization_id == organization_id
        assert audit_event.user_id == user_id

        assert audit_event.trace_id == trace_context.trace_id
        assert audit_event.request_id == trace_context.request_id
        assert audit_event.action_id == trace_context.action_id

        assert audit_event.event_type == "permission_denied"
        assert audit_event.resource_type == "permission"
        assert audit_event.resource_id == "knowledge.read"
        assert audit_event.metadata_json == {}
    finally:
        app.dependency_overrides.clear()