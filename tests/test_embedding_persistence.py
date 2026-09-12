import uuid

from app.db.session import SessionLocal
from app.embeddings.persistence import persist_chunk_embedding
from app.embeddings.provider import EmbeddingResult
from app.models.chunk_embedding import ChunkEmbedding
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_version import DocumentVersion
from app.models.organization import Organization
from sqlalchemy import func, select


def _create_document_chunk(
    *,
    organization_id: uuid.UUID,
    document_id: uuid.UUID,
    document_version_id: uuid.UUID,
    document_chunk_id: uuid.UUID,
) -> list[object]:
    return [
        Document(
            id=document_id,
            organization_id=organization_id,
            title="Embedding Test Document",
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
        DocumentChunk(
            id=document_chunk_id,
            organization_id=organization_id,
            document_version_id=document_version_id,
            chunk_index=0,
            content="Embedding test chunk",
            content_sha256="b" * 64,
        ),
    ]


def _embedding_result(
    *,
    model_name: str = "test-model",
) -> EmbeddingResult:
    return EmbeddingResult(
        model_name=model_name,
        dimensions=1536,
        vector=[1.0] + [0.0] * 1535,
    )


def test_persist_chunk_embedding_creates_embedding() -> None:
    organization_id = uuid.uuid4()
    document_id = uuid.uuid4()
    document_version_id = uuid.uuid4()
    document_chunk_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"EMBED-{organization_id.hex[:8]}",
                name="Embedding Persistence Test",
            )
        )
        db.add_all(
            _create_document_chunk(
                organization_id=organization_id,
                document_id=document_id,
                document_version_id=document_version_id,
                document_chunk_id=document_chunk_id,
            )
        )
        db.flush()

        result = persist_chunk_embedding(
            db,
            organization_id=organization_id,
            document_chunk_id=document_chunk_id,
            embedding=_embedding_result(),
        )

        stored_embedding = db.get(
            ChunkEmbedding,
            result.embedding_id,
        )

        assert stored_embedding is not None
        assert stored_embedding.organization_id == organization_id
        assert stored_embedding.document_chunk_id == document_chunk_id
        assert stored_embedding.embedding_model == "test-model"
        assert stored_embedding.dimensions == 1536
        assert result.created is True

        db.rollback()


def test_persist_chunk_embedding_does_not_create_duplicate() -> None:
    organization_id = uuid.uuid4()
    document_id = uuid.uuid4()
    document_version_id = uuid.uuid4()
    document_chunk_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"EMBED-DUP-{organization_id.hex[:8]}",
                name="Embedding Duplicate Test",
            )
        )
        db.add_all(
            _create_document_chunk(
                organization_id=organization_id,
                document_id=document_id,
                document_version_id=document_version_id,
                document_chunk_id=document_chunk_id,
            )
        )
        db.flush()

        first_result = persist_chunk_embedding(
            db,
            organization_id=organization_id,
            document_chunk_id=document_chunk_id,
            embedding=_embedding_result(),
        )

        second_result = persist_chunk_embedding(
            db,
            organization_id=organization_id,
            document_chunk_id=document_chunk_id,
            embedding=_embedding_result(),
        )

        embedding_count = db.scalar(
            select(func.count())
            .select_from(ChunkEmbedding)
            .where(
                ChunkEmbedding.document_chunk_id == document_chunk_id,
                ChunkEmbedding.embedding_model == "test-model",
            )
        )

        assert embedding_count == 1
        assert second_result.embedding_id == first_result.embedding_id
        assert first_result.created is True
        assert second_result.created is False

        db.rollback()


def test_persist_chunk_embedding_allows_different_models() -> None:
    organization_id = uuid.uuid4()
    document_id = uuid.uuid4()
    document_version_id = uuid.uuid4()
    document_chunk_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"EMBED-MODEL-{organization_id.hex[:8]}",
                name="Embedding Model Test",
            )
        )
        db.add_all(
            _create_document_chunk(
                organization_id=organization_id,
                document_id=document_id,
                document_version_id=document_version_id,
                document_chunk_id=document_chunk_id,
            )
        )
        db.flush()

        first_result = persist_chunk_embedding(
            db,
            organization_id=organization_id,
            document_chunk_id=document_chunk_id,
            embedding=_embedding_result(
                model_name="model-a",
            ),
        )

        second_result = persist_chunk_embedding(
            db,
            organization_id=organization_id,
            document_chunk_id=document_chunk_id,
            embedding=_embedding_result(
                model_name="model-b",
            ),
        )

        assert first_result.embedding_id != second_result.embedding_id
        assert first_result.created is True
        assert second_result.created is True

        db.rollback()


def test_persist_chunk_embedding_rejects_foreign_tenant_chunk() -> None:
    organization_a_id = uuid.uuid4()
    organization_b_id = uuid.uuid4()

    document_b_id = uuid.uuid4()
    document_version_b_id = uuid.uuid4()
    document_chunk_b_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add_all(
            [
                Organization(
                    id=organization_a_id,
                    code=f"EMBED-A-{organization_a_id.hex[:8]}",
                    name="Embedding Tenant A",
                ),
                Organization(
                    id=organization_b_id,
                    code=f"EMBED-B-{organization_b_id.hex[:8]}",
                    name="Embedding Tenant B",
                ),
            ]
        )
        db.add_all(
            _create_document_chunk(
                organization_id=organization_b_id,
                document_id=document_b_id,
                document_version_id=document_version_b_id,
                document_chunk_id=document_chunk_b_id,
            )
        )
        db.flush()

        try:
            persist_chunk_embedding(
                db,
                organization_id=organization_a_id,
                document_chunk_id=document_chunk_b_id,
                embedding=_embedding_result(),
            )
        except ValueError as exc:
            assert str(exc) == (
                "Document chunk does not belong to the organization."
            )
        else:
            raise AssertionError("Expected ValueError.")

        db.rollback()


def test_persist_chunk_embedding_does_not_commit_transaction() -> None:
    organization_id = uuid.uuid4()
    document_id = uuid.uuid4()
    document_version_id = uuid.uuid4()
    document_chunk_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"EMBED-TX-{organization_id.hex[:8]}",
                name="Embedding Transaction Test",
            )
        )
        db.add_all(
            _create_document_chunk(
                organization_id=organization_id,
                document_id=document_id,
                document_version_id=document_version_id,
                document_chunk_id=document_chunk_id,
            )
        )
        db.flush()

        result = persist_chunk_embedding(
            db,
            organization_id=organization_id,
            document_chunk_id=document_chunk_id,
            embedding=_embedding_result(),
        )

        embedding_id = result.embedding_id

        db.rollback()

        stored_embedding = db.get(
            ChunkEmbedding,
            embedding_id,
        )

        assert stored_embedding is None