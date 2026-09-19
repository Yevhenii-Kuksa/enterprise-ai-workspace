import uuid

from app.db.session import SessionLocal
from app.demo.knowledge import NEXALVORA_KNOWLEDGE_DOCUMENTS
from app.demo.knowledge_ingestion import (
    DEMO_KNOWLEDGE_SOURCE_SYSTEM,
    ingest_nexalvora_knowledge,
)
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_version import DocumentVersion
from app.models.organization import Organization
from sqlalchemy import func, select


def test_ingest_nexalvora_knowledge_creates_all_documents() -> None:
    organization_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"DEMO-KNOW-{organization_id.hex[:8]}",
                name="Demo Knowledge Test",
            )
        )
        db.flush()

        ingest_nexalvora_knowledge(
            db,
            organization_id=organization_id,
        )
        db.flush()

        document_count = db.scalar(
            select(func.count())
            .select_from(Document)
            .where(
                Document.organization_id == organization_id,
                Document.source_system
                == DEMO_KNOWLEDGE_SOURCE_SYSTEM,
            )
        )

        version_count = db.scalar(
            select(func.count())
            .select_from(DocumentVersion)
            .where(
                DocumentVersion.organization_id
                == organization_id
            )
        )

        chunk_count = db.scalar(
            select(func.count())
            .select_from(DocumentChunk)
            .where(
                DocumentChunk.organization_id
                == organization_id
            )
        )

        assert document_count == len(NEXALVORA_KNOWLEDGE_DOCUMENTS)
        assert version_count == len(NEXALVORA_KNOWLEDGE_DOCUMENTS)
        assert chunk_count is not None
        assert chunk_count >= len(NEXALVORA_KNOWLEDGE_DOCUMENTS)

        db.rollback()


def test_ingest_nexalvora_knowledge_is_idempotent() -> None:
    organization_id = uuid.uuid4()

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"DEMO-REPEAT-{organization_id.hex[:8]}",
                name="Demo Knowledge Repeat Test",
            )
        )
        db.flush()

        ingest_nexalvora_knowledge(
            db,
            organization_id=organization_id,
        )
        db.flush()

        first_document_count = db.scalar(
            select(func.count())
            .select_from(Document)
            .where(
                Document.organization_id == organization_id,
                Document.source_system
                == DEMO_KNOWLEDGE_SOURCE_SYSTEM,
            )
        )

        first_version_count = db.scalar(
            select(func.count())
            .select_from(DocumentVersion)
            .where(
                DocumentVersion.organization_id
                == organization_id
            )
        )

        first_chunk_count = db.scalar(
            select(func.count())
            .select_from(DocumentChunk)
            .where(
                DocumentChunk.organization_id
                == organization_id
            )
        )

        ingest_nexalvora_knowledge(
            db,
            organization_id=organization_id,
        )
        db.flush()

        second_document_count = db.scalar(
            select(func.count())
            .select_from(Document)
            .where(
                Document.organization_id == organization_id,
                Document.source_system
                == DEMO_KNOWLEDGE_SOURCE_SYSTEM,
            )
        )

        second_version_count = db.scalar(
            select(func.count())
            .select_from(DocumentVersion)
            .where(
                DocumentVersion.organization_id
                == organization_id
            )
        )

        second_chunk_count = db.scalar(
            select(func.count())
            .select_from(DocumentChunk)
            .where(
                DocumentChunk.organization_id
                == organization_id
            )
        )

        assert second_document_count == first_document_count
        assert second_version_count == first_version_count
        assert second_chunk_count == first_chunk_count

        db.rollback()