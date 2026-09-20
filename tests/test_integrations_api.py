import uuid
from datetime import UTC, datetime

from app.db.dependencies import get_db
from app.integrations.api_schemas import IntegrationSummaryResponse
from app.integrations.dependencies import (
    get_integration_catalog,
    get_integration_service,
)
from app.integrations.schemas import (
    IntegrationCapability,
    IntegrationKind,
    IntegrationRecord,
    IntegrationStatus,
)
from app.integrations.service import (
    IntegrationProviderFailureError,
    IntegrationProviderUnavailableError,
    IntegrationSourceMismatchError,
    IntegrationUnavailableError,
)
from app.main import app
from app.security.current_user import CurrentUser
from app.security.dependencies import get_current_user
from fastapi.testclient import TestClient


class FakeDb:
    def __init__(self) -> None:
        self.added: list[object] = []

    def add(
        self,
        obj: object,
    ) -> None:
        self.added.append(obj)

    def flush(
        self,
    ) -> None:
        pass

    def commit(
        self,
    ) -> None:
        pass


class FakeIntegrationCatalog:
    def list_integrations(
        self,
    ) -> list[IntegrationSummaryResponse]:
        return [
            IntegrationSummaryResponse(
                key="gmail",
                kind=IntegrationKind.EMAIL,
                provider="google",
                capabilities=(
                    IntegrationCapability.READ_MESSAGES,
                ),
                enabled=True,
                status=IntegrationStatus.READY,
            )
        ]


class FakeIntegrationService:
    def fetch_records(
        self,
        *,
        integration_key: str,
    ) -> list[IntegrationRecord]:
        assert integration_key == "gmail"

        return [
            IntegrationRecord(
                source_system="gmail",
                external_id="message-001",
                record_type="email_message",
                payload={
                    "subject": "Oferta",
                },
                source_url=(
                    "https://mail.google.com/mail/u/0/"
                    "#all/message-001"
                ),
                occurred_at=datetime(
                    2026,
                    9,
                    18,
                    10,
                    0,
                    tzinfo=UTC,
                ),
                fetched_at=datetime(
                    2026,
                    9,
                    18,
                    10,
                    5,
                    tzinfo=UTC,
                ),
            )
        ]


class UnavailableIntegrationService:
    def fetch_records(
        self,
        *,
        integration_key: str,
    ) -> list[IntegrationRecord]:
        raise IntegrationUnavailableError(
            f"Integration is not available: {integration_key}"
        )


class ProviderUnavailableIntegrationService:
    def fetch_records(
        self,
        *,
        integration_key: str,
    ) -> list[IntegrationRecord]:
        raise IntegrationProviderUnavailableError(
            f"Provider is not available: {integration_key}"
        )


class FailingIntegrationService:
    def fetch_records(
        self,
        *,
        integration_key: str,
    ) -> list[IntegrationRecord]:
        raise IntegrationProviderFailureError(
            f"Integration provider request failed: {integration_key}"
        )


class SourceMismatchIntegrationService:
    def fetch_records(
        self,
        *,
        integration_key: str,
    ) -> list[IntegrationRecord]:
        raise IntegrationSourceMismatchError(
            "Integration record source does not match "
            "the requested integration."
        )


def make_user(
    *,
    permissions: set[str],
) -> CurrentUser:
    return CurrentUser(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        department_id=None,
        is_active=True,
        permissions=permissions,
    )


def test_list_integrations_returns_200() -> None:
    user = make_user(
        permissions={
            "integration.read",
        }
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_integration_catalog] = (
        lambda: FakeIntegrationCatalog()
    )

    try:
        client = TestClient(app)

        response = client.get(
            "/api/integrations",
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    assert response.json() == [
        {
            "key": "gmail",
            "kind": "email",
            "provider": "google",
            "capabilities": [
                "read_messages",
            ],
            "enabled": True,
            "status": "ready",
        }
    ]


def test_list_integrations_returns_403_without_permission() -> None:
    fake_db = FakeDb()

    user = make_user(
        permissions=set(),
    )

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = lambda: user

    try:
        client = TestClient(app)

        response = client.get(
            "/api/integrations",
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert len(fake_db.added) == 1


def test_list_integration_records_returns_200() -> None:
    user = make_user(
        permissions={
            "integration.read",
        }
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_integration_service] = (
        lambda: FakeIntegrationService()
    )

    try:
        client = TestClient(app)

        response = client.get(
            "/api/integrations/gmail/records",
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    assert response.json() == [
        {
            "source_system": "gmail",
            "external_id": "message-001",
            "record_type": "email_message",
            "payload": {
                "subject": "Oferta",
            },
            "source_url": (
                "https://mail.google.com/mail/u/0/"
                "#all/message-001"
            ),
            "occurred_at": "2026-09-18T10:00:00Z",
            "fetched_at": "2026-09-18T10:05:00Z",
        }
    ]


def test_list_integration_records_returns_404_when_unavailable() -> None:
    user = make_user(
        permissions={
            "integration.read",
        }
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_integration_service] = (
        lambda: UnavailableIntegrationService()
    )

    try:
        client = TestClient(app)

        response = client.get(
            "/api/integrations/unknown/records",
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Integration is not available: unknown"
    }


def test_list_integration_records_returns_503_when_provider_unavailable() -> None:
    user = make_user(
        permissions={
            "integration.read",
        }
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_integration_service] = (
        lambda: ProviderUnavailableIntegrationService()
    )

    try:
        client = TestClient(app)

        response = client.get(
            "/api/integrations/gmail/records",
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Provider is not available: gmail"
    }


def test_integration_records_maps_provider_failure_to_502() -> None:
    user = make_user(
        permissions={
            "integration.read",
        }
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_integration_service] = (
        lambda: FailingIntegrationService()
    )

    try:
        client = TestClient(app)

        response = client.get(
            "/api/integrations/google-drive/records",
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json() == {
        "detail": (
            "Integration provider request failed: "
            "google-drive"
        )
    }


def test_list_integration_records_returns_502_on_source_mismatch() -> None:
    user = make_user(
        permissions={
            "integration.read",
        }
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_integration_service] = (
        lambda: SourceMismatchIntegrationService()
    )

    try:
        client = TestClient(app)

        response = client.get(
            "/api/integrations/gmail/records",
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json() == {
        "detail": (
            "Integration record source does not match "
            "the requested integration."
        )
    }