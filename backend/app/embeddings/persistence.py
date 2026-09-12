import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.embeddings.provider import EmbeddingResult
from app.models.chunk_embedding import ChunkEmbedding
from app.models.document_chunk import DocumentChunk


@dataclass(frozen=True, slots=True)
class PersistedEmbedding:
    embedding_id: uuid.UUID
    document_chunk_id: uuid.UUID
    embedding_model: str
    dimensions: int
    created: bool


def persist_chunk_embedding(
    session: Session,
    *,
    organization_id: uuid.UUID,
    document_chunk_id: uuid.UUID,
    embedding: EmbeddingResult,
) -> PersistedEmbedding:
    document_chunk = session.scalar(
        select(DocumentChunk).where(
            DocumentChunk.id == document_chunk_id,
            DocumentChunk.organization_id == organization_id,
        )
    )

    if document_chunk is None:
        raise ValueError(
            "Document chunk does not belong to the organization."
        )

    existing_embedding = session.scalar(
        select(ChunkEmbedding).where(
            ChunkEmbedding.organization_id == organization_id,
            ChunkEmbedding.document_chunk_id == document_chunk_id,
            ChunkEmbedding.embedding_model == embedding.model_name,
        )
    )

    if existing_embedding is not None:
        return PersistedEmbedding(
            embedding_id=existing_embedding.id,
            document_chunk_id=existing_embedding.document_chunk_id,
            embedding_model=existing_embedding.embedding_model,
            dimensions=existing_embedding.dimensions,
            created=False,
        )

    chunk_embedding = ChunkEmbedding(
        organization_id=organization_id,
        document_chunk_id=document_chunk_id,
        embedding_model=embedding.model_name,
        dimensions=embedding.dimensions,
        embedding=embedding.vector,
    )

    session.add(chunk_embedding)
    session.flush()

    return PersistedEmbedding(
        embedding_id=chunk_embedding.id,
        document_chunk_id=chunk_embedding.document_chunk_id,
        embedding_model=chunk_embedding.embedding_model,
        dimensions=chunk_embedding.dimensions,
        created=True,
    )