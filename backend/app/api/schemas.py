import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class RagQueryRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=4000,
    )


class RagCitationResponse(BaseModel):
    label: str
    document_title: str
    page_number: int | None
    section_title: str | None
    source_system: str | None
    source_uri: str | None


class RagReliabilityResponse(BaseModel):
    decision: Literal["allow", "degrade"]
    reasons: list[str]


class RagQueryResponse(BaseModel):
    answer: str
    model_name: str
    citations: list[RagCitationResponse]
    reliability: RagReliabilityResponse


class KnowledgeDocumentResponse(BaseModel):
    id: uuid.UUID
    department_id: uuid.UUID | None
    title: str
    source_type: str
    source_system: str | None
    external_id: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class KnowledgeDocumentVersionResponse(BaseModel):
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

class KnowledgeDocumentUploadResponse(BaseModel):
    document_id: uuid.UUID
    document_version_id: uuid.UUID | None
    version_number: int
    created_document: bool
    created_version: bool
    chunks_created: int
    embeddings_created: int