import uuid

from app.db.session import SessionLocal
from app.ingestion.chunk_persistence import persist_document_chunks
from app.ingestion.chunking import TextChunk
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_version import DocumentVersion
from app.models.organization import Organization
from sqlalchemy import select


def _create_version(
    *,
    organization_id: uuid.UUID,
    document_id: uuid.UUID,
    document_version_id: uuid.UUID,
) -> list[object]:
    return [
        Document(
            id=document_id,
            organization_id=organization_id,
            title="Chunk Persistence Document",
            source_type="upload",
        ),
        DocumentVersion(
            id=document_version_id,
            organization_id=organization_id,
            document_id=document_id,
            version_number=1,
            content_sha256="a" * 64,
            ingestion_status="completed",
        ),
    ]


def test_persist_document_chunks_creates_chunks() -> None:
    organization_id = uuid.uuid4()
    document_id = uuid.uuid4()
    document_version_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"CHUNK-{organization_id.hex[:8]}",
                name="Chunk Persistence Test",
            )
        )
        db.add_all(
            _create_version(
                organization_id=organization_id,
                document_id=document_id,
                document_version_id=document_version_id,
            )
        )
        db.flush()

        chunks = [
            TextChunk(
                chunk_index=0,
                content="Pierwszy fragment",
                content_sha256="b" * 64,
                token_count=10,
                page_number=1,
                section_title="Sekcja A",
                source_locator={"page": 1},
            ),
            TextChunk(
                chunk_index=1,
                content="Drugi fragment",
                content_sha256="c" * 64,
                token_count=12,
                page_number=2,
                section_title="Sekcja B",
                source_locator={"page": 2},
            ),
        ]

        persisted_chunks = persist_document_chunks(
            db,
            organization_id=organization_id,
            document_version_id=document_version_id,
            chunks=chunks,
        )

        stored_chunks = db.scalars(
            select(DocumentChunk)
            .where(
                DocumentChunk.document_version_id == document_version_id
            )
            .order_by(DocumentChunk.chunk_index)
        ).all()

        assert len(persisted_chunks) == 2
        assert len(stored_chunks) == 2

        assert persisted_chunks[0].document_chunk_id == stored_chunks[0].id
        assert persisted_chunks[0].chunk_index == 0
        assert persisted_chunks[0].content == "Pierwszy fragment"

        assert persisted_chunks[1].document_chunk_id == stored_chunks[1].id
        assert persisted_chunks[1].chunk_index == 1
        assert persisted_chunks[1].content == "Drugi fragment"

        assert stored_chunks[0].organization_id == organization_id
        assert stored_chunks[0].content_sha256 == "b" * 64
        assert stored_chunks[0].token_count == 10
        assert stored_chunks[0].page_number == 1
        assert stored_chunks[0].section_title == "Sekcja A"
        assert stored_chunks[0].source_locator == {"page": 1}

        db.rollback()


def test_persist_document_chunks_returns_empty_list_for_empty_input() -> None:
    organization_id = uuid.uuid4()
    document_id = uuid.uuid4()
    document_version_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"CHUNK-EMPTY-{organization_id.hex[:8]}",
                name="Chunk Empty Test",
            )
        )
        db.add_all(
            _create_version(
                organization_id=organization_id,
                document_id=document_id,
                document_version_id=document_version_id,
            )
        )
        db.flush()

        persisted_chunks = persist_document_chunks(
            db,
            organization_id=organization_id,
            document_version_id=document_version_id,
            chunks=[],
        )

        assert persisted_chunks == []

        db.rollback()


def test_persist_document_chunks_rejects_foreign_tenant_version() -> None:
    organization_a_id = uuid.uuid4()
    organization_b_id = uuid.uuid4()

    document_b_id = uuid.uuid4()
    document_version_b_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add_all(
            [
                Organization(
                    id=organization_a_id,
                    code=f"CHUNK-A-{organization_a_id.hex[:8]}",
                    name="Chunk Tenant A",
                ),
                Organization(
                    id=organization_b_id,
                    code=f"CHUNK-B-{organization_b_id.hex[:8]}",
                    name="Chunk Tenant B",
                ),
            ]
        )
        db.add_all(
            _create_version(
                organization_id=organization_b_id,
                document_id=document_b_id,
                document_version_id=document_version_b_id,
            )
        )
        db.flush()

        try:
            persist_document_chunks(
                db,
                organization_id=organization_a_id,
                document_version_id=document_version_b_id,
                chunks=[
                    TextChunk(
                        chunk_index=0,
                        content="Foreign chunk",
                        content_sha256="d" * 64,
                    )
                ],
            )
        except ValueError as exc:
            assert str(exc) == (
                "Document version does not belong to the organization."
            )
        else:
            raise AssertionError("Expected ValueError.")

        db.rollback()


def test_persist_document_chunks_does_not_commit_transaction() -> None:
    organization_id = uuid.uuid4()
    document_id = uuid.uuid4()
    document_version_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"CHUNK-TX-{organization_id.hex[:8]}",
                name="Chunk Transaction Test",
            )
        )
        db.add_all(
            _create_version(
                organization_id=organization_id,
                document_id=document_id,
                document_version_id=document_version_id,
            )
        )
        db.flush()

        persist_document_chunks(
            db,
            organization_id=organization_id,
            document_version_id=document_version_id,
            chunks=[
                TextChunk(
                    chunk_index=0,
                    content="Transactional chunk",
                    content_sha256="e" * 64,
                )
            ],
        )

        db.rollback()

        stored_chunks = db.scalars(
            select(DocumentChunk).where(
                DocumentChunk.document_version_id == document_version_id
            )
        ).all()

        assert stored_chunks == []