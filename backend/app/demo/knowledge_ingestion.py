from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.demo.ids import NEXALVORA_ORGANIZATION_ID
from app.demo.knowledge import NEXALVORA_KNOWLEDGE_DOCUMENTS
from app.demo.knowledge_content import NEXALVORA_KNOWLEDGE_CONTENT
from app.ingestion.pipeline import (
    TextIngestionRequest,
    ingest_text_document,
)

DEMO_KNOWLEDGE_SOURCE_SYSTEM = "nexalvora_demo"


def ingest_nexalvora_knowledge(
    db: Session,
    *,
    organization_id: UUID = NEXALVORA_ORGANIZATION_ID,
) -> None:
    for document in NEXALVORA_KNOWLEDGE_DOCUMENTS:
        ingest_text_document(
            db,
            TextIngestionRequest(
                organization_id=organization_id,
                title=document.title,
                source_type="demo",
                text=NEXALVORA_KNOWLEDGE_CONTENT[document.id],
                source_system=DEMO_KNOWLEDGE_SOURCE_SYSTEM,
                external_id=document.document_code,
                source_uri=(
                    f"demo://nexalvora/knowledge/"
                    f"{document.document_code}"
                ),
                mime_type="text/plain",
                source_modified_at=datetime(
                    2026,
                    9,
                    19,
                    10,
                    0,
                    tzinfo=UTC,
                ),
            ),
        )