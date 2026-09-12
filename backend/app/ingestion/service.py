import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_version import DocumentVersion


@dataclass(frozen=True, slots=True)
class IngestionRequest:
    organization_id: uuid.UUID
    title: str
    source_type: str
    content: bytes
    source_system: str | None = None
    external_id: str | None = None
    department_id: uuid.UUID | None = None
    source_uri: str | None = None
    mime_type: str | None = None
    source_modified_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class IngestionResolution:
    document_id: uuid.UUID
    document_version_id: uuid.UUID | None
    version_number: int
    is_new_document: bool
    is_new_version: bool


@dataclass(frozen=True, slots=True)
class IngestionPersistResult:
    document_id: uuid.UUID
    document_version_id: uuid.UUID | None
    version_number: int
    created_document: bool
    created_version: bool


def calculate_content_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def resolve_ingestion(
    session: Session,
    request: IngestionRequest,
) -> IngestionResolution:
    content_sha256 = calculate_content_sha256(request.content)

    document = session.scalar(
        select(Document).where(
            Document.organization_id == request.organization_id,
            Document.source_system == request.source_system,
            Document.external_id == request.external_id,
        )
    )

    if document is None:
        return IngestionResolution(
            document_id=uuid.uuid4(),
            document_version_id=uuid.uuid4(),
            version_number=1,
            is_new_document=True,
            is_new_version=True,
        )

    latest_version = session.scalar(
        select(DocumentVersion)
        .where(
            DocumentVersion.document_id == document.id,
            DocumentVersion.organization_id == request.organization_id,
        )
        .order_by(DocumentVersion.version_number.desc())
        .limit(1)
    )

    if latest_version is not None and latest_version.content_sha256 == content_sha256:
        return IngestionResolution(
            document_id=document.id,
            document_version_id=None,
            version_number=latest_version.version_number,
            is_new_document=False,
            is_new_version=False,
        )

    next_version_number = (
        1 if latest_version is None else latest_version.version_number + 1
    )

    return IngestionResolution(
        document_id=document.id,
        document_version_id=uuid.uuid4(),
        version_number=next_version_number,
        is_new_document=False,
        is_new_version=True,
    )


def persist_ingestion(
    session: Session,
    request: IngestionRequest,
) -> IngestionPersistResult:
    resolution = resolve_ingestion(session, request)

    if resolution.is_new_document:
        document = Document(
            id=resolution.document_id,
            organization_id=request.organization_id,
            department_id=request.department_id,
            title=request.title,
            source_type=request.source_type,
            source_system=request.source_system,
            external_id=request.external_id,
        )
        session.add(document)

    if not resolution.is_new_version:
        return IngestionPersistResult(
            document_id=resolution.document_id,
            document_version_id=None,
            version_number=resolution.version_number,
            created_document=False,
            created_version=False,
        )

    assert resolution.document_version_id is not None

    document_version = DocumentVersion(
        id=resolution.document_version_id,
        organization_id=request.organization_id,
        document_id=resolution.document_id,
        version_number=resolution.version_number,
        content_sha256=calculate_content_sha256(request.content),
        mime_type=request.mime_type,
        source_uri=request.source_uri,
        source_modified_at=request.source_modified_at,
        ingestion_status="pending",
    )

    session.add(document_version)
    session.flush()

    return IngestionPersistResult(
        document_id=resolution.document_id,
        document_version_id=resolution.document_version_id,
        version_number=resolution.version_number,
        created_document=resolution.is_new_document,
        created_version=True,
    )