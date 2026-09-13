import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ingestion.chunking import TextChunk
from app.models.document_chunk import DocumentChunk
from app.models.document_version import DocumentVersion


@dataclass(frozen=True, slots=True)
class PersistedDocumentChunk:
    document_chunk_id: uuid.UUID
    chunk_index: int
    content: str


def persist_document_chunks(
    session: Session,
    *,
    organization_id: uuid.UUID,
    document_version_id: uuid.UUID,
    chunks: list[TextChunk],
) -> list[PersistedDocumentChunk]:
    document_version = session.scalar(
        select(DocumentVersion).where(
            DocumentVersion.id == document_version_id,
            DocumentVersion.organization_id == organization_id,
        )
    )

    if document_version is None:
        raise ValueError(
            "Document version does not belong to the organization."
        )

    if not chunks:
        return []

    document_chunks = [
        DocumentChunk(
            organization_id=organization_id,
            document_version_id=document_version_id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            content_sha256=chunk.content_sha256,
            token_count=chunk.token_count,
            page_number=chunk.page_number,
            section_title=chunk.section_title,
            source_locator=chunk.source_locator,
        )
        for chunk in chunks
    ]

    session.add_all(document_chunks)
    session.flush()

    return [
        PersistedDocumentChunk(
            document_chunk_id=document_chunk.id,
            chunk_index=document_chunk.chunk_index,
            content=document_chunk.content,
        )
        for document_chunk in document_chunks
    ]