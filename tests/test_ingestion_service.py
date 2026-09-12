import uuid
from datetime import UTC, datetime

from app.db.session import SessionLocal
from app.ingestion.service import (
    IngestionRequest,
    calculate_content_sha256,
    persist_ingestion,
    resolve_ingestion,
)
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.organization import Organization
from sqlalchemy import delete, select


def test_calculate_content_sha256_is_deterministic() -> None:
    content = b"Enterprise AI Workspace"

    first_hash = calculate_content_sha256(content)
    second_hash = calculate_content_sha256(content)

    assert first_hash == second_hash


def test_calculate_content_sha256_changes_when_content_changes() -> None:
    first_hash = calculate_content_sha256(b"version 1")
    second_hash = calculate_content_sha256(b"version 2")

    assert first_hash != second_hash


def test_calculate_content_sha256_returns_64_character_hex_digest() -> None:
    content_hash = calculate_content_sha256(b"test content")

    assert len(content_hash) == 64
    assert all(character in "0123456789abcdef" for character in content_hash)


def test_resolve_ingestion_returns_new_document_for_unknown_source() -> None:
    organization_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"INGEST-NEW-{organization_id.hex[:8]}",
                name="Ingestion New Document Test",
            )
        )
        db.commit()

        request = IngestionRequest(
            organization_id=organization_id,
            title="New Document",
            source_type="upload",
            content=b"new document content",
            source_system="test",
            external_id="new-document",
        )

        resolution = resolve_ingestion(db, request)

        assert resolution.version_number == 1
        assert resolution.is_new_document is True
        assert resolution.is_new_version is True
        assert resolution.document_version_id is not None

        db.execute(
            delete(Organization).where(Organization.id == organization_id)
        )
        db.commit()


def test_resolve_ingestion_skips_duplicate_content() -> None:
    organization_id = uuid.uuid4()
    document_id = uuid.uuid4()
    version_id = uuid.uuid4()
    content = b"existing document content"

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"INGEST-DUP-{organization_id.hex[:8]}",
                name="Ingestion Duplicate Test",
            )
        )
        db.add(
            Document(
                id=document_id,
                organization_id=organization_id,
                title="Existing Document",
                source_type="upload",
                source_system="test",
                external_id="duplicate-document",
            )
        )
        db.add(
            DocumentVersion(
                id=version_id,
                organization_id=organization_id,
                document_id=document_id,
                version_number=1,
                content_sha256=calculate_content_sha256(content),
                ingestion_status="completed",
            )
        )
        db.commit()

        request = IngestionRequest(
            organization_id=organization_id,
            title="Existing Document",
            source_type="upload",
            content=content,
            source_system="test",
            external_id="duplicate-document",
        )

        resolution = resolve_ingestion(db, request)

        assert resolution.document_id == document_id
        assert resolution.document_version_id is None
        assert resolution.version_number == 1
        assert resolution.is_new_document is False
        assert resolution.is_new_version is False

        db.execute(
            delete(DocumentVersion).where(DocumentVersion.id == version_id)
        )
        db.execute(delete(Document).where(Document.id == document_id))
        db.execute(
            delete(Organization).where(Organization.id == organization_id)
        )
        db.commit()


def test_resolve_ingestion_creates_next_version_for_changed_content() -> None:
    organization_id = uuid.uuid4()
    document_id = uuid.uuid4()
    version_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"INGEST-VER-{organization_id.hex[:8]}",
                name="Ingestion Version Test",
            )
        )
        db.add(
            Document(
                id=document_id,
                organization_id=organization_id,
                title="Versioned Document",
                source_type="upload",
                source_system="test",
                external_id="versioned-document",
            )
        )
        db.add(
            DocumentVersion(
                id=version_id,
                organization_id=organization_id,
                document_id=document_id,
                version_number=1,
                content_sha256=calculate_content_sha256(b"version 1"),
                ingestion_status="completed",
            )
        )
        db.commit()

        request = IngestionRequest(
            organization_id=organization_id,
            title="Versioned Document",
            source_type="upload",
            content=b"version 2",
            source_system="test",
            external_id="versioned-document",
        )

        resolution = resolve_ingestion(db, request)

        assert resolution.document_id == document_id
        assert resolution.document_version_id is not None
        assert resolution.version_number == 2
        assert resolution.is_new_document is False
        assert resolution.is_new_version is True

        db.execute(
            delete(DocumentVersion).where(DocumentVersion.id == version_id)
        )
        db.execute(delete(Document).where(Document.id == document_id))
        db.execute(
            delete(Organization).where(Organization.id == organization_id)
        )
        db.commit()


def test_resolve_ingestion_isolates_documents_by_tenant() -> None:
    organization_a_id = uuid.uuid4()
    organization_b_id = uuid.uuid4()
    document_b_id = uuid.uuid4()
    version_b_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add_all(
            [
                Organization(
                    id=organization_a_id,
                    code=f"INGEST-A-{organization_a_id.hex[:8]}",
                    name="Ingestion Tenant A",
                ),
                Organization(
                    id=organization_b_id,
                    code=f"INGEST-B-{organization_b_id.hex[:8]}",
                    name="Ingestion Tenant B",
                ),
                Document(
                    id=document_b_id,
                    organization_id=organization_b_id,
                    title="Foreign Document",
                    source_type="upload",
                    source_system="test",
                    external_id="shared-external-id",
                ),
                DocumentVersion(
                    id=version_b_id,
                    organization_id=organization_b_id,
                    document_id=document_b_id,
                    version_number=1,
                    content_sha256=calculate_content_sha256(b"foreign content"),
                    ingestion_status="completed",
                ),
            ]
        )
        db.commit()

        request = IngestionRequest(
            organization_id=organization_a_id,
            title="Tenant A Document",
            source_type="upload",
            content=b"tenant a content",
            source_system="test",
            external_id="shared-external-id",
        )

        resolution = resolve_ingestion(db, request)

        assert resolution.document_id != document_b_id
        assert resolution.version_number == 1
        assert resolution.is_new_document is True
        assert resolution.is_new_version is True

        db.execute(
            delete(DocumentVersion).where(DocumentVersion.id == version_b_id)
        )
        db.execute(delete(Document).where(Document.id == document_b_id))
        db.execute(
            delete(Organization).where(
                Organization.id.in_(
                    [organization_a_id, organization_b_id]
                )
            )
        )
        db.commit()


def test_persist_ingestion_creates_document_and_version() -> None:
    organization_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"PERSIST-NEW-{organization_id.hex[:8]}",
                name="Persist New Document Test",
            )
        )
        db.flush()

        request = IngestionRequest(
            organization_id=organization_id,
            title="Persisted Document",
            source_type="upload",
            content=b"persisted content",
            source_system="test",
            external_id="persisted-document",
        )

        result = persist_ingestion(db, request)

        document = db.get(Document, result.document_id)
        assert document is not None
        assert document.title == "Persisted Document"
        assert document.organization_id == organization_id

        assert result.document_version_id is not None
        version = db.get(DocumentVersion, result.document_version_id)

        assert version is not None
        assert version.document_id == result.document_id
        assert version.version_number == 1
        assert version.ingestion_status == "pending"
        assert result.created_document is True
        assert result.created_version is True

        db.rollback()


def test_persist_ingestion_preserves_version_metadata() -> None:
    organization_id = uuid.uuid4()
    source_modified_at = datetime(2026, 9, 12, 12, 30, tzinfo=UTC)

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"PERSIST-META-{organization_id.hex[:8]}",
                name="Persist Metadata Test",
            )
        )
        db.flush()

        request = IngestionRequest(
            organization_id=organization_id,
            title="Metadata Document",
            source_type="sharepoint",
            content=b"metadata content",
            source_system="sharepoint",
            external_id="metadata-document",
            source_uri="https://example.test/document.pdf",
            mime_type="application/pdf",
            source_modified_at=source_modified_at,
        )

        result = persist_ingestion(db, request)

        assert result.document_version_id is not None
        version = db.get(DocumentVersion, result.document_version_id)

        assert version is not None
        assert version.mime_type == "application/pdf"
        assert version.source_uri == "https://example.test/document.pdf"
        assert version.source_modified_at == source_modified_at

        db.rollback()


def test_persist_ingestion_does_not_create_duplicate_version() -> None:
    organization_id = uuid.uuid4()
    content = b"duplicate persisted content"

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"PERSIST-DUP-{organization_id.hex[:8]}",
                name="Persist Duplicate Test",
            )
        )
        db.flush()

        request = IngestionRequest(
            organization_id=organization_id,
            title="Duplicate Document",
            source_type="upload",
            content=content,
            source_system="test",
            external_id="duplicate-persisted-document",
        )

        first_result = persist_ingestion(db, request)
        second_result = persist_ingestion(db, request)

        versions = db.scalars(
            select(DocumentVersion).where(
                DocumentVersion.document_id == first_result.document_id
            )
        ).all()

        assert len(versions) == 1
        assert first_result.created_document is True
        assert first_result.created_version is True
        assert second_result.document_id == first_result.document_id
        assert second_result.document_version_id is None
        assert second_result.created_document is False
        assert second_result.created_version is False

        db.rollback()


def test_persist_ingestion_creates_next_version_for_changed_content() -> None:
    organization_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"PERSIST-VER-{organization_id.hex[:8]}",
                name="Persist Version Test",
            )
        )
        db.flush()

        first_request = IngestionRequest(
            organization_id=organization_id,
            title="Versioned Persisted Document",
            source_type="upload",
            content=b"persisted version 1",
            source_system="test",
            external_id="persisted-version-document",
        )

        second_request = IngestionRequest(
            organization_id=organization_id,
            title="Versioned Persisted Document",
            source_type="upload",
            content=b"persisted version 2",
            source_system="test",
            external_id="persisted-version-document",
        )

        first_result = persist_ingestion(db, first_request)
        second_result = persist_ingestion(db, second_request)

        versions = db.scalars(
            select(DocumentVersion)
            .where(
                DocumentVersion.document_id == first_result.document_id
            )
            .order_by(DocumentVersion.version_number)
        ).all()

        assert len(versions) == 2
        assert versions[0].version_number == 1
        assert versions[1].version_number == 2

        assert second_result.document_id == first_result.document_id
        assert second_result.document_version_id is not None
        assert second_result.version_number == 2
        assert second_result.created_document is False
        assert second_result.created_version is True

        db.rollback()