import uuid
from dataclasses import dataclass

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.chunk_embedding import ChunkEmbedding
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_version import DocumentVersion
from app.security.current_user import CurrentUser


@dataclass(frozen=True, slots=True)
class VectorSearchResult:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_version_id: uuid.UUID
    document_title: str
    content: str
    chunk_index: int
    distance: float
    page_number: int | None
    section_title: str | None
    source_locator: dict[str, object] | None
    source_system: str | None
    source_uri: str | None


def search_similar_chunks(
    session: Session,
    *,
    current_user: CurrentUser,
    query_embedding: list[float],
    embedding_model: str,
    limit: int = 10,
) -> list[VectorSearchResult]:
    if limit <= 0:
        raise ValueError("Search limit must be greater than zero.")
        
    if not current_user.is_active:
        raise PermissionError("Inactive user cannot perform vector search.")

    distance = ChunkEmbedding.embedding.cosine_distance(query_embedding)

    document_access_filter = or_(
        Document.department_id.is_(None),
        Document.department_id == current_user.department_id,
    )

    statement = (
        select(
            DocumentChunk.id.label("chunk_id"),
            Document.id.label("document_id"),
            DocumentChunk.document_version_id,
            Document.title.label("document_title"),
            DocumentChunk.content,
            DocumentChunk.chunk_index,
            distance.label("distance"),
            DocumentChunk.page_number,
            DocumentChunk.section_title,
            DocumentChunk.source_locator,
            Document.source_system,
            DocumentVersion.source_uri,
        )
        .join(
            ChunkEmbedding,
            ChunkEmbedding.document_chunk_id == DocumentChunk.id,
        )
        .join(
            DocumentVersion,
            DocumentVersion.id == DocumentChunk.document_version_id,
        )
        .join(
            Document,
            Document.id == DocumentVersion.document_id,
        )
        .where(
            DocumentChunk.organization_id == current_user.organization_id,
            ChunkEmbedding.organization_id == current_user.organization_id,
            DocumentVersion.organization_id == current_user.organization_id,
            Document.organization_id == current_user.organization_id,
            document_access_filter,
            ChunkEmbedding.embedding_model == embedding_model,
        )
        .order_by(distance)
        .limit(limit)
    )

    rows = session.execute(statement).all()

    return [
        VectorSearchResult(
            chunk_id=row.chunk_id,
            document_id=row.document_id,
            document_version_id=row.document_version_id,
            document_title=row.document_title,
            content=row.content,
            chunk_index=row.chunk_index,
            distance=float(row.distance),
            page_number=row.page_number,
            section_title=row.section_title,
            source_locator=row.source_locator,
            source_system=row.source_system,
            source_uri=row.source_uri,
        )
        for row in rows
    ]