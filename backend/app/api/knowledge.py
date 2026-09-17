import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.schemas import (
    KnowledgeDocumentResponse,
    KnowledgeDocumentUploadResponse,
    KnowledgeDocumentVersionResponse,
)
from app.audit.service import record_audit_event
from app.core.config import Settings, get_settings
from app.core.trace_context import TraceContext
from app.core.trace_dependencies import get_trace_context
from app.db.dependencies import get_db
from app.embeddings.factory import create_embedding_provider
from app.ingestion.file_ingestion import (
    FileIngestionRequest,
    ingest_document_file,
)
from app.knowledge.service import (
    KnowledgeDocument,
    KnowledgeDocumentVersion,
    get_document,
    list_document_versions,
    list_documents,
    validate_department_access,
)
from app.security.current_user import CurrentUser
from app.security.dependencies import get_current_user

router = APIRouter(
    prefix="/api/knowledge",
    tags=["Knowledge Hub"],
)

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
settings_dependency = Depends(get_settings)
trace_context_dependency = Depends(get_trace_context)


def _document_response(
    document: KnowledgeDocument,
) -> KnowledgeDocumentResponse:
    return KnowledgeDocumentResponse(
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


def _version_response(
    version: KnowledgeDocumentVersion,
) -> KnowledgeDocumentVersionResponse:
    return KnowledgeDocumentVersionResponse(
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


@router.post(
    "/documents",
    response_model=KnowledgeDocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    title: Annotated[
        str,
        Form(
            min_length=1,
            max_length=500,
        ),
    ],
    file: Annotated[
        UploadFile,
        File(),
    ],
    department_id: Annotated[
        uuid.UUID | None,
        Form(),
    ] = None,
    source_system: Annotated[
        str | None,
        Form(
            max_length=100,
        ),
    ] = "upload",
    external_id: Annotated[
        str | None,
        Form(
            max_length=255,
        ),
    ] = None,
    source_uri: Annotated[
        str | None,
        Form(
            max_length=1000,
        ),
    ] = None,
    db: Session = db_dependency,
    current_user: CurrentUser = current_user_dependency,
    settings: Settings = settings_dependency,
    trace_context: TraceContext = trace_context_dependency,
) -> KnowledgeDocumentUploadResponse:
    try:
        validate_department_access(
            db,
            current_user=current_user,
            department_id=department_id,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    if file.filename is None or not file.filename.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Filename is required.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Uploaded file must not be empty.",
        )

    embedding_provider = create_embedding_provider(
        settings,
    )

    try:
        result = ingest_document_file(
            db,
            FileIngestionRequest(
                organization_id=current_user.organization_id,
                title=title.strip(),
                source_type="upload",
                filename=file.filename,
                content=content,
                source_system=source_system,
                external_id=external_id,
                department_id=department_id,
                source_uri=source_uri,
                mime_type=file.content_type,
            ),
            embedding_provider=embedding_provider,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    record_audit_event(
        db,
        current_user=current_user,
        trace_context=trace_context,
        event_type="knowledge_document_uploaded",
        resource_type="document",
        resource_id=str(result.document_id),
        metadata={
            "created_document": result.created_document,
            "created_version": result.created_version,
            "version_number": result.version_number,
            "chunks_created": result.chunks_created,
            "embeddings_created": result.embeddings_created,
        },
    )

    db.commit()

    return KnowledgeDocumentUploadResponse(
        document_id=result.document_id,
        document_version_id=result.document_version_id,
        version_number=result.version_number,
        created_document=result.created_document,
        created_version=result.created_version,
        chunks_created=result.chunks_created,
        embeddings_created=result.embeddings_created,
    )


@router.get(
    "/documents",
    response_model=list[KnowledgeDocumentResponse],
)
def get_documents(
    search: str | None = Query(
        default=None,
        max_length=500,
    ),
    db: Session = db_dependency,
    current_user: CurrentUser = current_user_dependency,
    trace_context: TraceContext = trace_context_dependency,
) -> list[KnowledgeDocumentResponse]:
    documents = list_documents(
        db,
        current_user=current_user,
        search=search,
    )

    record_audit_event(
        db,
        current_user=current_user,
        trace_context=trace_context,
        event_type="knowledge_search",
        resource_type="document",
        metadata={
            "search_used": bool(
                search is not None and search.strip()
            ),
            "result_count": len(documents),
        },
    )

    db.commit()

    return [
        _document_response(document)
        for document in documents
    ]


@router.get(
    "/documents/{document_id}",
    response_model=KnowledgeDocumentResponse,
)
def get_document_details(
    document_id: uuid.UUID,
    db: Session = db_dependency,
    current_user: CurrentUser = current_user_dependency,
    trace_context: TraceContext = trace_context_dependency,
) -> KnowledgeDocumentResponse:
    document = get_document(
        db,
        current_user=current_user,
        document_id=document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    record_audit_event(
        db,
        current_user=current_user,
        trace_context=trace_context,
        event_type="knowledge_document_viewed",
        resource_type="document",
        resource_id=str(document_id),
        metadata={},
    )

    db.commit()

    return _document_response(document)


@router.get(
    "/documents/{document_id}/versions",
    response_model=list[KnowledgeDocumentVersionResponse],
)
def get_document_versions(
    document_id: uuid.UUID,
    db: Session = db_dependency,
    current_user: CurrentUser = current_user_dependency,
    trace_context: TraceContext = trace_context_dependency,
) -> list[KnowledgeDocumentVersionResponse]:
    document = get_document(
        db,
        current_user=current_user,
        document_id=document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    versions = list_document_versions(
        db,
        current_user=current_user,
        document_id=document_id,
    )

    record_audit_event(
        db,
        current_user=current_user,
        trace_context=trace_context,
        event_type="knowledge_document_versions_viewed",
        resource_type="document",
        resource_id=str(document_id),
        metadata={
            "version_count": len(versions),
        },
    )

    db.commit()

    return [
        _version_response(version)
        for version in versions
    ]