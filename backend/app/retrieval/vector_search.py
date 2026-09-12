import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk_embedding import ChunkEmbedding
from app.models.document_chunk import DocumentChunk


@dataclass(frozen=True, slots=True)
class VectorSearchResult:
    chunk_id: uuid.UUID
    document_version_id: uuid.UUID
    content: str
    chunk_index: int
    distance: float
    page_number: int | None
    section_title: str | None
    source_locator: dict[str, object] | None


def search_similar_chunks(
    session: Session,
    *,
    organization_id: uuid.UUID,
    query_embedding: list[float],
    embedding_model: str,
    limit: int = 10,
) -> list[VectorSearchResult]:
    distance = ChunkEmbedding.embedding.cosine_distance(query_embedding)

    statement = (
        select(
            DocumentChunk.id,
            DocumentChunk.document_version_id,
            DocumentChunk.content,
            DocumentChunk.chunk_index,
            distance.label("distance"),
            DocumentChunk.page_number,
            DocumentChunk.section_title,
            DocumentChunk.source_locator,
        )
        .join(
            ChunkEmbedding,
            ChunkEmbedding.document_chunk_id == DocumentChunk.id,
        )
        .where(
            DocumentChunk.organization_id == organization_id,
            ChunkEmbedding.organization_id == organization_id,
            ChunkEmbedding.embedding_model == embedding_model,
        )
        .order_by(distance)
        .limit(limit)
    )

    rows = session.execute(statement).all()

    return [
        VectorSearchResult(
            chunk_id=row.id,
            document_version_id=row.document_version_id,
            content=row.content,
            chunk_index=row.chunk_index,
            distance=float(row.distance),
            page_number=row.page_number,
            section_title=row.section_title,
            source_locator=row.source_locator,
        )
        for row in rows
    ]