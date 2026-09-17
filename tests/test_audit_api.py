import uuid
from datetime import UTC, datetime
from unittest.mock import patch

from app.db.dependencies import get_db
from app.main import app
from app.models.audit_event import AuditEvent
from app.security.current_user import CurrentUser
from app.security.dependencies import get_current_user
from fastapi.testclient import TestClient

ORGANIZATION_ID = uuid.uuid4()
USER_ID = uuid.uuid4()
EVENT_ID = uuid.uuid4()
TRACE_ID = uuid.uuid4()
REQUEST_ID = uuid.uuid4()

CREATED_AT = datetime(
    2026,
    9,
    17,
    12,
    0,
    tzinfo=UTC,
)

CREATED_AT_JSON = "2026-09-17T12:00:00Z"


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


def _override_db() -> FakeDb:
    return FakeDb()


def _audit_reader() -> CurrentUser:
    return CurrentUser(
        id=USER_ID,
        organization_id=ORGANIZATION_ID,
        is_active=True,
        permissions={"audit.read"},
    )


def _user_without_audit_permission() -> CurrentUser:
    return CurrentUser(
        id=USER_ID,
        organization_id=ORGANIZATION_ID,
        is_active=True,
        permissions={"knowledge.read"},
    )


def _audit_event() -> AuditEvent:
    return AuditEvent(
        id=EVENT_ID,
        organization_id=ORGANIZATION_ID,
        user_id=USER_ID,
        trace_id=TRACE_ID,
        request_id=REQUEST_ID,
        action_id=None,
        event_type="knowledge_search",
        resource_type="document",
        resource_id="document-123",
        metadata_json={"result_count": 3},
        created_at=CREATED_AT,
    )


def test_list_audit_events_returns_audit_contract() -> None:
    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _audit_reader

    try:
        with patch(
            "app.api.audit.list_audit_events",
            return_value=[_audit_event()],
        ) as mocked_list_audit_events:
            client = TestClient(app)

            response = client.get(
                "/api/audit/events",
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    assert response.json() == [
        {
            "id": str(EVENT_ID),
            "organization_id": str(ORGANIZATION_ID),
            "user_id": str(USER_ID),
            "trace_id": str(TRACE_ID),
            "request_id": str(REQUEST_ID),
            "action_id": None,
            "event_type": "knowledge_search",
            "resource_type": "document",
            "resource_id": "document-123",
            "metadata_json": {
                "result_count": 3,
            },
            "created_at": CREATED_AT_JSON,
        }
    ]

    mocked_list_audit_events.assert_called_once()

    call = mocked_list_audit_events.call_args

    assert (
        call.kwargs["current_user"].organization_id
        == ORGANIZATION_ID
    )
    assert "audit.read" in call.kwargs["current_user"].permissions


def test_list_audit_events_requires_audit_read_permission() -> None:
    fake_db = FakeDb()

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = (
        _user_without_audit_permission
    )

    try:
        with patch(
            "app.api.audit.list_audit_events",
        ) as mocked_list_audit_events:
            client = TestClient(app)

            response = client.get(
                "/api/audit/events",
                headers={
                    "X-Trace-ID": str(TRACE_ID),
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Permission denied.",
    }

    mocked_list_audit_events.assert_not_called()

    assert fake_db.flushed is True
    assert fake_db.committed is True
    assert len(fake_db.added) == 1

    audit_event = fake_db.added[0]

    assert isinstance(audit_event, AuditEvent)

    assert audit_event.organization_id == ORGANIZATION_ID
    assert audit_event.user_id == USER_ID

    assert audit_event.trace_id == TRACE_ID
    assert (
        str(audit_event.request_id)
        == response.headers["X-Request-ID"]
    )
    assert audit_event.action_id is None

    assert audit_event.event_type == "permission_denied"
    assert audit_event.resource_type == "permission"
    assert audit_event.resource_id == "audit.read"
    assert audit_event.metadata_json == {}


def test_list_audit_events_passes_filters_to_service() -> None:
    filter_user_id = uuid.uuid4()

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _audit_reader

    try:
        with patch(
            "app.api.audit.list_audit_events",
            return_value=[],
        ) as mocked_list_audit_events:
            client = TestClient(app)

            response = client.get(
                "/api/audit/events",
                params={
                    "event_type": "rag_query",
                    "user_id": str(filter_user_id),
                    "created_from": "2026-09-01T00:00:00Z",
                    "created_to": "2026-09-30T23:59:59Z",
                    "limit": 50,
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == []

    call = mocked_list_audit_events.call_args

    assert call.kwargs["event_type"] == "rag_query"
    assert call.kwargs["user_id"] == filter_user_id
    assert call.kwargs["created_from"] == datetime(
        2026,
        9,
        1,
        0,
        0,
        tzinfo=UTC,
    )
    assert call.kwargs["created_to"] == datetime(
        2026,
        9,
        30,
        23,
        59,
        59,
        tzinfo=UTC,
    )
    assert call.kwargs["limit"] == 50


def test_list_audit_events_rejects_limit_over_500() -> None:
    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _audit_reader

    try:
        with patch(
            "app.api.audit.list_audit_events",
        ) as mocked_list_audit_events:
            client = TestClient(app)

            response = client.get(
                "/api/audit/events",
                params={
                    "limit": 501,
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    mocked_list_audit_events.assert_not_called()