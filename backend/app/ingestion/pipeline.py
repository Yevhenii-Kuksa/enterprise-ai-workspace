import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.embeddings.persistence import persist_chunk_embedding
from app.embeddings.provider import EmbeddingProvider
from app.embeddings.service import generate_embeddings
from app.ingestion.chunk_persistence import persist_document_chunks
from app.ingestion.chunking import ChunkingConfig, TextChunk, chunk_text
from app.ingestion.service import (
    IngestionRequest,
    persist_ingestion,
    resolve_ingestion,
)


@dataclass(frozen=True, slots=True)
class TextIngestionRequest:
    organization_id: uuid.UUID
    title: str
    source_type: str
    text: str
    source_system: str | None = None
    external_id: str | None = None
    department_id: uuid.UUID | None = None
    source_uri: str | None = None
    mime_type: str | None = None
    source_modified_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class TextIngestionResult:
    document_id: uuid.UUID
    document_version_id: uuid.UUID | None
    version_number: int
    created_document: bool
    created_version: bool
    chunks_created: int
    embeddings_created: int


def to_ingestion_request(
    request: TextIngestionRequest,
) -> IngestionRequest:
    return IngestionRequest(
        organization_id=request.organization_id,
        title=request.title,
        source_type=request.source_type,
        content=request.text.encode("utf-8"),
        source_system=request.source_system,
        external_id=request.external_id,
        department_id=request.department_id,
        source_uri=request.source_uri,
        mime_type=request.mime_type,
        source_modified_at=request.source_modified_at,
    )


def resolve_text_ingestion(
    session: Session,
    request: TextIngestionRequest,
) -> TextIngestionResult | None:
    ingestion_request = to_ingestion_request(request)
    resolution = resolve_ingestion(
        session,
        ingestion_request,
    )

    if resolution.is_new_version:
        return None

    return TextIngestionResult(
        document_id=resolution.document_id,
        document_version_id=None,
        version_number=resolution.version_number,
        created_document=False,
        created_version=False,
        chunks_created=0,
        embeddings_created=0,
    )


def _persist_chunks_and_embeddings(
    session: Session,
    *,
    request: TextIngestionRequest,
    document_version_id: uuid.UUID,
    chunks: list[TextChunk],
    embedding_provider: EmbeddingProvider | None,
) -> tuple[int, int]:
    persisted_chunks = persist_document_chunks(
        session,
        organization_id=request.organization_id,
        document_version_id=document_version_id,
        chunks=chunks,
    )

    embeddings_created = 0

    if embedding_provider is not None and persisted_chunks:
        embeddings = generate_embeddings(
            embedding_provider,
            [chunk.content for chunk in persisted_chunks],
        )

        if len(embeddings) != len(persisted_chunks):
            raise RuntimeError(
                "Embedding count does not match persisted chunk count."
            )

        for persisted_chunk, embedding in zip(
            persisted_chunks,
            embeddings,
            strict=True,
        ):
            persisted_embedding = persist_chunk_embedding(
                session,
                organization_id=request.organization_id,
                document_chunk_id=persisted_chunk.document_chunk_id,
                embedding=embedding,
            )

            if persisted_embedding.created:
                embeddings_created += 1

    return len(persisted_chunks), embeddings_created


def ingest_prepared_chunks(
    session: Session,
    request: TextIngestionRequest,
    *,
    chunks: list[TextChunk],
    embedding_provider: EmbeddingProvider | None = None,
) -> TextIngestionResult:
    duplicate_result = resolve_text_ingestion(
        session,
        request,
    )

    if duplicate_result is not None:
        return duplicate_result

    ingestion_request = to_ingestion_request(request)
    persisted = persist_ingestion(
        session,
        ingestion_request,
    )

    if persisted.document_version_id is None:
        raise RuntimeError(
            "Expected a document version for non-duplicate ingestion."
        )

    chunks_created, embeddings_created = _persist_chunks_and_embeddings(
        session,
        request=request,
        document_version_id=persisted.document_version_id,
        chunks=chunks,
        embedding_provider=embedding_provider,
    )

    return TextIngestionResult(
        document_id=persisted.document_id,
        document_version_id=persisted.document_version_id,
        version_number=persisted.version_number,
        created_document=persisted.created_document,
        created_version=persisted.created_version,
        chunks_created=chunks_created,
        embeddings_created=embeddings_created,
    )


def ingest_text_document(
    session: Session,
    request: TextIngestionRequest,
    *,
    embedding_provider: EmbeddingProvider | None = None,
    chunking_config: ChunkingConfig | None = None,
) -> TextIngestionResult:
    chunks = chunk_text(
        request.text,
        config=chunking_config,
    )

    return ingest_prepared_chunks(
        session,
        request,
        chunks=chunks,
        embedding_provider=embedding_provider,
    )