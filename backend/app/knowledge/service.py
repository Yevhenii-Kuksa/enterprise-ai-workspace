import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.models.department import Department
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.security.current_user import CurrentUser


@dataclass(frozen=True, slots=True)
class KnowledgeDocument:
    id: uuid.UUID
    department_id: uuid.UUID | None
    title: str
    source_type: str
    source_system: str | None
    external_id: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class KnowledgeDocumentVersion:
    id: uuid.UUID
    document_id: uuid.UUID
    version_number: int
    mime_type: str | None
    source_uri: str | None
    ingestion_status: str
    ingestion_error: str | None
    source_modified_at: datetime | None
    ingested_at: datetime | None
    created_at: datetime


def _document_access_filter(
    current_user: CurrentUser,
) -> ColumnElement[bool]:
    return or_(
        Document.department_id.is_(None),
        Document.department_id == current_user.department_id,
    )


def _to_knowledge_document(
    document: Document,
) -> KnowledgeDocument:
    return KnowledgeDocument(
        id=document.id,
        department_id=document.department_id,
        title=document.title,
        source_type=document.source_type,
        source_system=document.source_system,
        external_id=document.external_id,
        is_active=document.is_active,
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


def _to_knowledge_document_version(
    version: DocumentVersion,
) -> KnowledgeDocumentVersion:
    return KnowledgeDocumentVersion(
        id=version.id,
        document_id=version.document_id,
        version_number=version.version_number,
        mime_type=version.mime_type,
        source_uri=version.source_uri,
        ingestion_status=version.ingestion_status,
        ingestion_error=version.ingestion_error,
        source_modified_at=version.source_modified_at,
        ingested_at=version.ingested_at,
        created_at=version.created_at,
    )


def validate_department_access(
    session: Session,
    *,
    current_user: CurrentUser,
    department_id: uuid.UUID | None,
) -> None:
    if not current_user.is_active:
        raise PermissionError(
            "Inactive user cannot access the Knowledge Hub."
        )

    if department_id is None:
        return

    department = session.scalar(
        select(Department).where(
            Department.id == department_id,
            Department.organization_id
            == current_user.organization_id,
        )
    )

    if department is None:
        raise ValueError(
            "Department does not belong to the organization."
        )

    if (
        current_user.department_id is not None
        and department_id != current_user.department_id
    ):
        raise PermissionError(
            "User cannot manage documents for this department."
        )


def list_documents(
    session: Session,
    *,
    current_user: CurrentUser,
    search: str | None = None,
    include_inactive: bool = False,
) -> list[KnowledgeDocument]:
    if not current_user.is_active:
        raise PermissionError(
            "Inactive user cannot access the Knowledge Hub."
        )

    statement = select(Document).where(
        Document.organization_id == current_user.organization_id,
        _document_access_filter(current_user),
    )

    if not include_inactive:
        statement = statement.where(
            Document.is_active.is_(True)
        )

    if search is not None:
        normalized_search = search.strip()

        if normalized_search:
            statement = statement.where(
                Document.title.ilike(
                    f"%{normalized_search}%"
                )
            )

    statement = statement.order_by(
        Document.title,
        Document.id,
    )

    documents = session.scalars(statement).all()

    return [
        _to_knowledge_document(document)
        for document in documents
    ]


def get_document(
    session: Session,
    *,
    current_user: CurrentUser,
    document_id: uuid.UUID,
) -> KnowledgeDocument | None:
    if not current_user.is_active:
        raise PermissionError(
            "Inactive user cannot access the Knowledge Hub."
        )

    document = session.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.organization_id
            == current_user.organization_id,
            _document_access_filter(current_user),
        )
    )

    if document is None:
        return None

    return _to_knowledge_document(document)


def list_document_versions(
    session: Session,
    *,
    current_user: CurrentUser,
    document_id: uuid.UUID,
) -> list[KnowledgeDocumentVersion]:
    document = get_document(
        session,
        current_user=current_user,
        document_id=document_id,
    )

    if document is None:
        return []

    versions = session.scalars(
        select(DocumentVersion)
        .where(
            DocumentVersion.document_id == document_id,
            DocumentVersion.organization_id
            == current_user.organization_id,
        )
        .order_by(
            DocumentVersion.version_number.desc()
        )
    ).all()

    return [
        _to_knowledge_document_version(version)
        for version in versions
    ]