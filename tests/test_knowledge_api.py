import uuid
from datetime import UTC, datetime
from unittest.mock import patch

from app.db.dependencies import get_db
from app.ingestion.pipeline import TextIngestionResult
from app.knowledge.service import (
    KnowledgeDocument,
    KnowledgeDocumentVersion,
)
from app.main import app
from app.models.audit_event import AuditEvent
from app.security.current_user import CurrentUser
from app.security.dependencies import get_current_user
from fastapi.testclient import TestClient

DOCUMENT_ID = uuid.uuid4()
DEPARTMENT_ID = uuid.uuid4()
VERSION_ID = uuid.uuid4()

CREATED_AT = datetime(
    2026,
    9,
    16,
    10,
    0,
    tzinfo=UTC,
)

UPDATED_AT = datetime(
    2026,
    9,
    16,
    11,
    0,
    tzinfo=UTC,
)

CREATED_AT_JSON = "2026-09-16T10:00:00Z"
UPDATED_AT_JSON = "2026-09-16T11:00:00Z"


def _current_user() -> CurrentUser:
    return CurrentUser(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        department_id=DEPARTMENT_ID,
        is_active=True,
        permissions=set(),
    )


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


def _document() -> KnowledgeDocument:
    return KnowledgeDocument(
        id=DOCUMENT_ID,
        department_id=DEPARTMENT_ID,
        title="Procedura magazynowa",
        source_type="upload",
        source_system="upload",
        external_id="procedura-magazynowa",
        is_active=True,
        created_at=CREATED_AT,
        updated_at=UPDATED_AT,
    )


def _version() -> KnowledgeDocumentVersion:
    return KnowledgeDocumentVersion(
        id=VERSION_ID,
        document_id=DOCUMENT_ID,
        version_number=2,
        mime_type="application/pdf",
        source_uri="https://example.test/procedura.pdf",
        ingestion_status="completed",
        ingestion_error=None,
        source_modified_at=CREATED_AT,
        ingested_at=UPDATED_AT,
        created_at=CREATED_AT,
    )


def test_list_documents_returns_knowledge_contract() -> None:
    fake_db = FakeDb()

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = _current_user

    try:
        with patch(
            "app.api.knowledge.list_documents",
            return_value=[_document()],
        ) as mocked_list_documents:
            client = TestClient(app)

            response = client.get(
                "/api/knowledge/documents",
                params={
                    "search": "magazyn",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    assert response.json() == [
        {
            "id": str(DOCUMENT_ID),
            "department_id": str(DEPARTMENT_ID),
            "title": "Procedura magazynowa",
            "source_type": "upload",
            "source_system": "upload",
            "external_id": "procedura-magazynowa",
            "is_active": True,
            "created_at": CREATED_AT_JSON,
            "updated_at": UPDATED_AT_JSON,
        }
    ]

    mocked_list_documents.assert_called_once()

    call = mocked_list_documents.call_args

    assert call.kwargs["search"] == "magazyn"
    assert call.kwargs["current_user"].department_id == DEPARTMENT_ID

    assert fake_db.flushed is True
    assert fake_db.committed is True
    assert len(fake_db.added) == 1

    audit_event = fake_db.added[0]

    assert isinstance(audit_event, AuditEvent)
    assert audit_event.event_type == "knowledge_search"
    assert audit_event.resource_type == "document"
    assert audit_event.resource_id is None
    assert audit_event.metadata_json == {
        "search_used": True,
        "result_count": 1,
    }

    audit_metadata = str(audit_event.metadata_json)

    assert "magazyn" not in audit_metadata
    assert "Procedura magazynowa" not in audit_metadata


def test_get_document_returns_document_details() -> None:
    fake_db = FakeDb()

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = _current_user

    try:
        with patch(
            "app.api.knowledge.get_document",
            return_value=_document(),
        ):
            client = TestClient(app)

            response = client.get(
                f"/api/knowledge/documents/{DOCUMENT_ID}"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    assert response.json()["id"] == str(DOCUMENT_ID)
    assert response.json()["title"] == "Procedura magazynowa"
    assert response.json()["department_id"] == str(DEPARTMENT_ID)

    assert fake_db.flushed is True
    assert fake_db.committed is True
    assert len(fake_db.added) == 1

    audit_event = fake_db.added[0]

    assert isinstance(audit_event, AuditEvent)
    assert audit_event.event_type == "knowledge_document_viewed"
    assert audit_event.resource_type == "document"
    assert audit_event.resource_id == str(DOCUMENT_ID)
    assert audit_event.metadata_json == {}


def test_get_document_returns_404_when_document_is_inaccessible() -> None:
    fake_db = FakeDb()

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = _current_user

    try:
        with patch(
            "app.api.knowledge.get_document",
            return_value=None,
        ):
            client = TestClient(app)

            response = client.get(
                f"/api/knowledge/documents/{DOCUMENT_ID}"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document not found.",
    }

    assert fake_db.added == []
    assert fake_db.committed is False


def test_get_document_versions_returns_version_history() -> None:
    fake_db = FakeDb()

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = _current_user

    try:
        with (
            patch(
                "app.api.knowledge.get_document",
                return_value=_document(),
            ),
            patch(
                "app.api.knowledge.list_document_versions",
                return_value=[_version()],
            ),
        ):
            client = TestClient(app)

            response = client.get(
                f"/api/knowledge/documents/{DOCUMENT_ID}/versions"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    assert response.json() == [
        {
            "id": str(VERSION_ID),
            "document_id": str(DOCUMENT_ID),
            "version_number": 2,
            "mime_type": "application/pdf",
            "source_uri": "https://example.test/procedura.pdf",
            "ingestion_status": "completed",
            "ingestion_error": None,
            "source_modified_at": CREATED_AT_JSON,
            "ingested_at": UPDATED_AT_JSON,
            "created_at": CREATED_AT_JSON,
        }
    ]

    assert fake_db.flushed is True
    assert fake_db.committed is True
    assert len(fake_db.added) == 1

    audit_event = fake_db.added[0]

    assert isinstance(audit_event, AuditEvent)
    assert (
        audit_event.event_type
        == "knowledge_document_versions_viewed"
    )
    assert audit_event.resource_type == "document"
    assert audit_event.resource_id == str(DOCUMENT_ID)
    assert audit_event.metadata_json == {
        "version_count": 1,
    }

    assert (
        "https://example.test/procedura.pdf"
        not in str(audit_event.metadata_json)
    )


def test_get_document_versions_returns_404_for_inaccessible_document() -> None:
    fake_db = FakeDb()

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = _current_user

    try:
        with patch(
            "app.api.knowledge.get_document",
            return_value=None,
        ):
            client = TestClient(app)

            response = client.get(
                f"/api/knowledge/documents/{DOCUMENT_ID}/versions"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document not found.",
    }

    assert fake_db.added == []
    assert fake_db.committed is False


def test_list_documents_rejects_search_over_500_characters() -> None:
    fake_db = FakeDb()

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = _current_user

    try:
        client = TestClient(app)

        response = client.get(
            "/api/knowledge/documents",
            params={
                "search": "a" * 501,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert fake_db.added == []
    assert fake_db.committed is False


def test_upload_document_uses_current_user_organization() -> None:
    current_user = _current_user()
    document_id = uuid.uuid4()
    version_id = uuid.uuid4()
    fake_db = FakeDb()

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = lambda: current_user

    try:
        with (
            patch(
                "app.api.knowledge.validate_department_access",
            ) as mocked_validate_department,
            patch(
                "app.api.knowledge.create_embedding_provider",
                return_value=object(),
            ),
            patch(
                "app.api.knowledge.ingest_document_file",
                return_value=TextIngestionResult(
                    document_id=document_id,
                    document_version_id=version_id,
                    version_number=1,
                    created_document=True,
                    created_version=True,
                    chunks_created=3,
                    embeddings_created=3,
                ),
            ) as mocked_ingest,
        ):
            client = TestClient(app)

            response = client.post(
                "/api/knowledge/documents",
                data={
                    "title": "Procedura magazynowa",
                    "source_system": "upload",
                    "external_id": "procedura-001",
                },
                files={
                    "file": (
                        "procedura.txt",
                        "TreЕ›Д‡ procedury magazynowej.".encode(),
                        "text/plain",
                    ),
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201

    assert response.json() == {
        "document_id": str(document_id),
        "document_version_id": str(version_id),
        "version_number": 1,
        "created_document": True,
        "created_version": True,
        "chunks_created": 3,
        "embeddings_created": 3,
    }

    mocked_validate_department.assert_called_once()

    request = mocked_ingest.call_args.args[1]

    assert request.organization_id == current_user.organization_id
    assert request.title == "Procedura magazynowa"
    assert request.filename == "procedura.txt"
    assert request.content == "TreЕ›Д‡ procedury magazynowej.".encode()
    assert request.source_type == "upload"
    assert request.external_id == "procedura-001"

    assert fake_db.flushed is True
    assert fake_db.committed is True
    assert len(fake_db.added) == 1

    audit_event = fake_db.added[0]

    assert isinstance(audit_event, AuditEvent)
    assert audit_event.event_type == "knowledge_document_uploaded"
    assert audit_event.resource_type == "document"
    assert audit_event.resource_id == str(document_id)
    assert audit_event.metadata_json == {
        "created_document": True,
        "created_version": True,
        "version_number": 1,
        "chunks_created": 3,
        "embeddings_created": 3,
    }

    audit_metadata = str(audit_event.metadata_json)

    assert "Procedura magazynowa" not in audit_metadata
    assert "procedura.txt" not in audit_metadata
    assert "procedura-001" not in audit_metadata
    assert "TreЕ›Д‡ procedury magazynowej." not in audit_metadata


def test_upload_document_rejects_empty_file() -> None:
    fake_db = FakeDb()

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = _current_user

    try:
        with (
            patch(
                "app.api.knowledge.validate_department_access",
            ),
            patch(
                "app.api.knowledge.create_embedding_provider",
            ) as mocked_provider,
        ):
            client = TestClient(app)

            response = client.post(
                "/api/knowledge/documents",
                data={
                    "title": "Pusty dokument",
                },
                files={
                    "file": (
                        "empty.txt",
                        b"",
                        "text/plain",
                    ),
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Uploaded file must not be empty.",
    }

    mocked_provider.assert_not_called()

    assert fake_db.added == []
    assert fake_db.committed is False


def test_upload_document_maps_ingestion_error_to_422() -> None:
    fake_db = FakeDb()

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = _current_user

    try:
        with (
            patch(
                "app.api.knowledge.validate_department_access",
            ),
            patch(
                "app.api.knowledge.create_embedding_provider",
                return_value=object(),
            ),
            patch(
                "app.api.knowledge.ingest_document_file",
                side_effect=ValueError(
                    "Unsupported document type."
                ),
            ),
        ):
            client = TestClient(app)

            response = client.post(
                "/api/knowledge/documents",
                data={
                    "title": "NieobsЕ‚ugiwany dokument",
                },
                files={
                    "file": (
                        "document.xyz",
                        b"content",
                        "application/octet-stream",
                    ),
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Unsupported document type.",
    }

    assert fake_db.added == []
    assert fake_db.committed is False


def test_upload_document_validates_requested_department() -> None:
    department_id = uuid.uuid4()
    fake_db = FakeDb()

    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = _current_user

    try:
        with patch(
            "app.api.knowledge.validate_department_access",
            side_effect=PermissionError(
                "User cannot manage documents for this department."
            ),
        ) as mocked_validate_department:
            client = TestClient(app)

            response = client.post(
                "/api/knowledge/documents",
                data={
                    "title": "Dokument HR",
                    "department_id": str(department_id),
                },
                files={
                    "file": (
                        "hr.txt",
                        "TreЕ›Д‡ dokumentu HR.".encode(),
                        "text/plain",
                    ),
                },
            )
    finally:
        app.dependency_overrides.clear()

    mocked_validate_department.assert_called_once()

    assert response.status_code == 403
    assert response.json() == {
        "detail": "User cannot manage documents for this department.",
    }

    assert fake_db.added == []
    assert fake_db.committed is False