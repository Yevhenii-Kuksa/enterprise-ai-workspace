import uuid

from app.db.session import SessionLocal
from app.ingestion.chunking import ChunkingConfig
from app.ingestion.pipeline import (
    TextIngestionRequest,
    ingest_text_document,
)
from app.models.chunk_embedding import ChunkEmbedding
from app.models.document_chunk import DocumentChunk
from app.models.organization import Organization
from sqlalchemy import func, select


class FakeEmbeddingProvider:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    @property
    def model_name(self) -> str:
        return "fake-model"

    @property
    def dimensions(self) -> int:
        return 1536

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        self.calls.append(texts)

        vectors: list[list[float]] = []

        for index, _text in enumerate(texts):
            vector = [0.0] * 1536
            vector[index] = 1.0
            vectors.append(vector)

        return vectors


def test_ingest_text_document_creates_embeddings_for_chunks() -> None:
    organization_id = uuid.uuid4()
    provider = FakeEmbeddingProvider()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"PIPE-EMBED-{organization_id.hex[:8]}",
                name="Pipeline Embedding Test",
            )
        )
        db.flush()

        request = TextIngestionRequest(
            organization_id=organization_id,
            title="Dokument embeddingowy",
            source_type="upload",
            text="abcdefghij",
            source_system="test",
            external_id="pipeline-embedding-document",
        )

        result = ingest_text_document(
            db,
            request,
            embedding_provider=provider,
            chunking_config=ChunkingConfig(
                max_characters=6,
                overlap_characters=2,
            ),
        )

        assert result.document_version_id is not None
        assert result.chunks_created == 2
        assert result.embeddings_created == 2

        assert provider.calls == [
            [
                "abcdef",
                "efghij",
            ]
        ]

        stored_chunks = db.scalars(
            select(DocumentChunk)
            .where(
                DocumentChunk.document_version_id
                == result.document_version_id
            )
            .order_by(DocumentChunk.chunk_index)
        ).all()

        assert len(stored_chunks) == 2

        stored_embeddings = db.scalars(
            select(ChunkEmbedding)
            .where(
                ChunkEmbedding.organization_id == organization_id
            )
            .order_by(ChunkEmbedding.created_at)
        ).all()

        assert len(stored_embeddings) == 2

        embedding_chunk_ids = {
            embedding.document_chunk_id
            for embedding in stored_embeddings
        }

        assert embedding_chunk_ids == {
            stored_chunks[0].id,
            stored_chunks[1].id,
        }

        assert all(
            embedding.embedding_model == "fake-model"
            for embedding in stored_embeddings
        )
        assert all(
            embedding.dimensions == 1536
            for embedding in stored_embeddings
        )

        db.rollback()


def test_duplicate_ingestion_does_not_call_embedding_provider() -> None:
    organization_id = uuid.uuid4()
    provider = FakeEmbeddingProvider()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"PIPE-EMBED-DUP-{organization_id.hex[:8]}",
                name="Pipeline Embedding Duplicate Test",
            )
        )
        db.flush()

        request = TextIngestionRequest(
            organization_id=organization_id,
            title="Dokument bez duplikacji embeddingów",
            source_type="upload",
            text="abcdefghij",
            source_system="test",
            external_id="pipeline-embedding-duplicate",
        )

        first_result = ingest_text_document(
            db,
            request,
            embedding_provider=provider,
            chunking_config=ChunkingConfig(
                max_characters=6,
                overlap_characters=2,
            ),
        )

        second_result = ingest_text_document(
            db,
            request,
            embedding_provider=provider,
            chunking_config=ChunkingConfig(
                max_characters=6,
                overlap_characters=2,
            ),
        )

        assert first_result.embeddings_created == 2
        assert second_result.embeddings_created == 0

        assert provider.calls == [
            [
                "abcdef",
                "efghij",
            ]
        ]

        embedding_count = db.scalar(
            select(func.count())
            .select_from(ChunkEmbedding)
            .where(
                ChunkEmbedding.organization_id == organization_id
            )
        )

        assert embedding_count == 2

        db.rollback()


def test_embedding_pipeline_does_not_commit_transaction() -> None:
    organization_id = uuid.uuid4()
    provider = FakeEmbeddingProvider()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"PIPE-EMBED-TX-{organization_id.hex[:8]}",
                name="Pipeline Embedding Transaction Test",
            )
        )
        db.flush()

        request = TextIngestionRequest(
            organization_id=organization_id,
            title="Dokument transakcyjny embeddingów",
            source_type="upload",
            text="abcdefghij",
            source_system="test",
            external_id=f"pipeline-embedding-tx-{uuid.uuid4()}",
        )

        result = ingest_text_document(
            db,
            request,
            embedding_provider=provider,
            chunking_config=ChunkingConfig(
                max_characters=6,
                overlap_characters=2,
            ),
        )

        assert result.embeddings_created == 2

        db.rollback()

        stored_embeddings = db.scalar(
            select(func.count())
            .select_from(ChunkEmbedding)
            .where(
                ChunkEmbedding.organization_id == organization_id
            )
        )

        assert stored_embeddings == 0