import uuid
from datetime import UTC, datetime

from app.db.session import SessionLocal
from app.ingestion.chunking import ChunkingConfig
from app.ingestion.pipeline import (
    TextIngestionRequest,
    ingest_text_document,
    resolve_text_ingestion,
    to_ingestion_request,
)
from app.ingestion.service import calculate_content_sha256
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_version import DocumentVersion
from app.models.organization import Organization
from sqlalchemy import delete, func, select


def test_to_ingestion_request_encodes_text_as_utf8_bytes() -> None:
    request = TextIngestionRequest(
        organization_id=uuid.uuid4(),
        title="Dokument",
        source_type="upload",
        text="Zażółć gęślą jaźń",
    )

    ingestion_request = to_ingestion_request(request)

    assert ingestion_request.content == "Zażółć gęślą jaźń".encode()


def test_to_ingestion_request_preserves_tenant_and_department() -> None:
    organization_id = uuid.uuid4()
    department_id = uuid.uuid4()

    request = TextIngestionRequest(
        organization_id=organization_id,
        department_id=department_id,
        title="Procedura",
        source_type="sharepoint",
        text="Treść dokumentu",
    )

    ingestion_request = to_ingestion_request(request)

    assert ingestion_request.organization_id == organization_id
    assert ingestion_request.department_id == department_id


def test_to_ingestion_request_preserves_source_metadata() -> None:
    source_modified_at = datetime(
        2026,
        9,
        13,
        10,
        30,
        tzinfo=UTC,
    )

    request = TextIngestionRequest(
        organization_id=uuid.uuid4(),
        title="Instrukcja",
        source_type="sharepoint",
        text="Treść instrukcji",
        source_system="sharepoint",
        external_id="document-123",
        source_uri="https://example.test/document-123",
        mime_type="text/plain",
        source_modified_at=source_modified_at,
    )

    ingestion_request = to_ingestion_request(request)

    assert ingestion_request.title == "Instrukcja"
    assert ingestion_request.source_type == "sharepoint"
    assert ingestion_request.source_system == "sharepoint"
    assert ingestion_request.external_id == "document-123"
    assert ingestion_request.source_uri == "https://example.test/document-123"
    assert ingestion_request.mime_type == "text/plain"
    assert ingestion_request.source_modified_at == source_modified_at


def test_resolve_text_ingestion_short_circuits_duplicate_content() -> None:
    organization_id = uuid.uuid4()
    document_id = uuid.uuid4()
    document_version_id = uuid.uuid4()
    content = "Treść istniejącego dokumentu"

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"PIPE-DUP-{organization_id.hex[:8]}",
                name="Pipeline Duplicate Test",
            )
        )
        db.add(
            Document(
                id=document_id,
                organization_id=organization_id,
                title="Istniejący dokument",
                source_type="upload",
                source_system="test",
                external_id="pipeline-duplicate",
            )
        )
        db.add(
            DocumentVersion(
                id=document_version_id,
                organization_id=organization_id,
                document_id=document_id,
                version_number=1,
                content_sha256=calculate_content_sha256(
                    content.encode()
                ),
                ingestion_status="completed",
            )
        )
        db.commit()

        request = TextIngestionRequest(
            organization_id=organization_id,
            title="Istniejący dokument",
            source_type="upload",
            text=content,
            source_system="test",
            external_id="pipeline-duplicate",
        )

        result = resolve_text_ingestion(db, request)

        assert result is not None
        assert result.document_id == document_id
        assert result.document_version_id is None
        assert result.version_number == 1
        assert result.created_document is False
        assert result.created_version is False
        assert result.chunks_created == 0
        assert result.embeddings_created == 0

        db.execute(
            delete(DocumentVersion).where(
                DocumentVersion.id == document_version_id
            )
        )
        db.execute(
            delete(Document).where(
                Document.id == document_id
            )
        )
        db.execute(
            delete(Organization).where(
                Organization.id == organization_id
            )
        )
        db.commit()


def test_ingest_text_document_creates_document_version_and_chunks() -> None:
    organization_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"PIPE-NEW-{organization_id.hex[:8]}",
                name="Pipeline New Document Test",
            )
        )
        db.flush()

        request = TextIngestionRequest(
            organization_id=organization_id,
            title="Nowy dokument",
            source_type="upload",
            text="abcdefghij",
            source_system="test",
            external_id="pipeline-new-document",
            mime_type="text/plain",
        )

        result = ingest_text_document(
            db,
            request,
            chunking_config=ChunkingConfig(
                max_characters=6,
                overlap_characters=2,
            ),
        )

        assert result.created_document is True
        assert result.created_version is True
        assert result.version_number == 1
        assert result.document_version_id is not None
        assert result.chunks_created == 2
        assert result.embeddings_created == 0

        stored_chunks = db.scalars(
            select(DocumentChunk)
            .where(
                DocumentChunk.document_version_id
                == result.document_version_id
            )
            .order_by(DocumentChunk.chunk_index)
        ).all()

        assert [chunk.content for chunk in stored_chunks] == [
            "abcdef",
            "efghij",
        ]

        db.rollback()


def test_ingest_text_document_does_not_duplicate_chunks() -> None:
    organization_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"PIPE-REPEAT-{organization_id.hex[:8]}",
                name="Pipeline Repeat Test",
            )
        )
        db.flush()

        request = TextIngestionRequest(
            organization_id=organization_id,
            title="Powtarzany dokument",
            source_type="upload",
            text="abcdefghij",
            source_system="test",
            external_id="pipeline-repeat-document",
        )

        first_result = ingest_text_document(
            db,
            request,
            chunking_config=ChunkingConfig(
                max_characters=6,
                overlap_characters=2,
            ),
        )

        second_result = ingest_text_document(
            db,
            request,
            chunking_config=ChunkingConfig(
                max_characters=6,
                overlap_characters=2,
            ),
        )

        chunk_count = db.scalar(
            select(func.count())
            .select_from(DocumentChunk)
            .where(
                DocumentChunk.document_version_id
                == first_result.document_version_id
            )
        )

        assert first_result.chunks_created == 2
        assert second_result.created_document is False
        assert second_result.created_version is False
        assert second_result.chunks_created == 0
        assert second_result.embeddings_created == 0
        assert chunk_count == 2

        db.rollback()


def test_ingest_text_document_creates_new_version_for_changed_text() -> None:
    organization_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"PIPE-VER-{organization_id.hex[:8]}",
                name="Pipeline Version Test",
            )
        )
        db.flush()

        first_request = TextIngestionRequest(
            organization_id=organization_id,
            title="Dokument wersjonowany",
            source_type="upload",
            text="abcdefghij",
            source_system="test",
            external_id="pipeline-version-document",
        )

        second_request = TextIngestionRequest(
            organization_id=organization_id,
            title="Dokument wersjonowany",
            source_type="upload",
            text="klmnopqrst",
            source_system="test",
            external_id="pipeline-version-document",
        )

        first_result = ingest_text_document(
            db,
            first_request,
            chunking_config=ChunkingConfig(
                max_characters=6,
                overlap_characters=2,
            ),
        )

        second_result = ingest_text_document(
            db,
            second_request,
            chunking_config=ChunkingConfig(
                max_characters=6,
                overlap_characters=2,
            ),
        )

        assert first_result.version_number == 1
        assert second_result.version_number == 2
        assert second_result.created_document is False
        assert second_result.created_version is True
        assert second_result.document_version_id is not None
        assert (
            second_result.document_version_id
            != first_result.document_version_id
        )
        assert second_result.chunks_created == 2

        versions = db.scalars(
            select(DocumentVersion)
            .where(
                DocumentVersion.document_id
                == first_result.document_id
            )
            .order_by(DocumentVersion.version_number)
        ).all()

        assert [version.version_number for version in versions] == [1, 2]

        db.rollback()


def test_ingest_text_document_does_not_commit_transaction() -> None:
    organization_id = uuid.uuid4()
    external_id = f"pipeline-tx-{uuid.uuid4()}"

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"PIPE-TX-{organization_id.hex[:8]}",
                name="Pipeline Transaction Test",
            )
        )
        db.flush()

        request = TextIngestionRequest(
            organization_id=organization_id,
            title="Dokument transakcyjny",
            source_type="upload",
            text="Treść dokumentu transakcyjnego",
            source_system="test",
            external_id=external_id,
        )

        ingest_text_document(
            db,
            request,
        )

        db.rollback()

        stored_document = db.scalar(
            select(Document).where(
                Document.organization_id == organization_id,
                Document.source_system == "test",
                Document.external_id == external_id,
            )
        )

        assert stored_document is None