import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.embeddings.provider import EmbeddingProvider
from app.ingestion.chunking import ChunkingConfig
from app.ingestion.file_parser import (
    FileParseRequest,
    parse_document_file,
)
from app.ingestion.parsing import chunk_parsed_document
from app.ingestion.pipeline import (
    TextIngestionRequest,
    TextIngestionResult,
    ingest_prepared_chunks,
)


@dataclass(frozen=True, slots=True)
class FileIngestionRequest:
    organization_id: uuid.UUID
    title: str
    source_type: str
    filename: str
    content: bytes
    source_system: str | None = None
    external_id: str | None = None
    department_id: uuid.UUID | None = None
    source_uri: str | None = None
    mime_type: str | None = None
    source_modified_at: datetime | None = None


def ingest_document_file(
    session: Session,
    request: FileIngestionRequest,
    *,
    embedding_provider: EmbeddingProvider | None = None,
    chunking_config: ChunkingConfig | None = None,
) -> TextIngestionResult:
    parsed = parse_document_file(
        FileParseRequest(
            filename=request.filename,
            content=request.content,
            mime_type=request.mime_type,
        )
    )

    chunks = chunk_parsed_document(
        parsed,
        config=chunking_config,
    )

    if not chunks:
        raise ValueError(
            "Parsed document did not produce any chunks."
        )

    text_request = TextIngestionRequest(
        organization_id=request.organization_id,
        title=request.title,
        source_type=request.source_type,
        text=parsed.text,
        source_system=request.source_system,
        external_id=request.external_id,
        department_id=request.department_id,
        source_uri=request.source_uri,
        mime_type=parsed.mime_type,
        source_modified_at=request.source_modified_at,
    )

    return ingest_prepared_chunks(
        session,
        text_request,
        chunks=chunks,
        embedding_provider=embedding_provider,
    )