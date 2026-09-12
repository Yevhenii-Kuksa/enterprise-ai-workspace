import uuid

from app.db.session import SessionLocal
from app.models.chunk_embedding import ChunkEmbedding
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_version import DocumentVersion
from app.models.organization import Organization
from app.retrieval.vector_search import search_similar_chunks
from sqlalchemy import delete


def test_vector_search_ranks_and_isolates_by_tenant() -> None:
    organization_a_id = uuid.uuid4()
    organization_b_id = uuid.uuid4()

    document_a_id = uuid.uuid4()
    document_b_id = uuid.uuid4()

    version_a_id = uuid.uuid4()
    version_b_id = uuid.uuid4()

    chunk_a_near_id = uuid.uuid4()
    chunk_a_far_id = uuid.uuid4()
    chunk_b_id = uuid.uuid4()

    embedding_a_near_id = uuid.uuid4()
    embedding_a_far_id = uuid.uuid4()
    embedding_b_id = uuid.uuid4()

    query_embedding = [1.0, 0.0, 0.0] + [0.0] * 1533
    near_embedding = [0.99, 0.01, 0.0] + [0.0] * 1533
    far_embedding = [0.0, 1.0, 0.0] + [0.0] * 1533
    foreign_embedding = [1.0, 0.0, 0.0] + [0.0] * 1533

    with SessionLocal() as db:
        db.add_all(
            [
                Organization(
                    id=organization_a_id,
                    code=f"TEST-A-{organization_a_id.hex[:8]}",
                    name="Test Organization A",
                ),
                Organization(
                    id=organization_b_id,
                    code=f"TEST-B-{organization_b_id.hex[:8]}",
                    name="Test Organization B",
                ),
                Document(
                    id=document_a_id,
                    organization_id=organization_a_id,
                    title="Document A",
                    source_type="upload",
                ),
                Document(
                    id=document_b_id,
                    organization_id=organization_b_id,
                    title="Document B",
                    source_type="upload",
                ),
                DocumentVersion(
                    id=version_a_id,
                    organization_id=organization_a_id,
                    document_id=document_a_id,
                    version_number=1,
                    content_sha256="a" * 64,
                    ingestion_status="completed",
                ),
                DocumentVersion(
                    id=version_b_id,
                    organization_id=organization_b_id,
                    document_id=document_b_id,
                    version_number=1,
                    content_sha256="b" * 64,
                    ingestion_status="completed",
                ),
                DocumentChunk(
                    id=chunk_a_near_id,
                    organization_id=organization_a_id,
                    document_version_id=version_a_id,
                    chunk_index=0,
                    content="Near chunk",
                    content_sha256="c" * 64,
                ),
                DocumentChunk(
                    id=chunk_a_far_id,
                    organization_id=organization_a_id,
                    document_version_id=version_a_id,
                    chunk_index=1,
                    content="Far chunk",
                    content_sha256="d" * 64,
                ),
                DocumentChunk(
                    id=chunk_b_id,
                    organization_id=organization_b_id,
                    document_version_id=version_b_id,
                    chunk_index=0,
                    content="Foreign tenant chunk",
                    content_sha256="e" * 64,
                ),
                ChunkEmbedding(
                    id=embedding_a_near_id,
                    organization_id=organization_a_id,
                    document_chunk_id=chunk_a_near_id,
                    embedding_model="test-model",
                    dimensions=1536,
                    embedding=near_embedding,
                ),
                ChunkEmbedding(
                    id=embedding_a_far_id,
                    organization_id=organization_a_id,
                    document_chunk_id=chunk_a_far_id,
                    embedding_model="test-model",
                    dimensions=1536,
                    embedding=far_embedding,
                ),
                ChunkEmbedding(
                    id=embedding_b_id,
                    organization_id=organization_b_id,
                    document_chunk_id=chunk_b_id,
                    embedding_model="test-model",
                    dimensions=1536,
                    embedding=foreign_embedding,
                ),
            ]
        )
        db.commit()

        results = search_similar_chunks(
            db,
            organization_id=organization_a_id,
            query_embedding=query_embedding,
            embedding_model="test-model",
            limit=10,
        )

        assert [result.chunk_id for result in results] == [
            chunk_a_near_id,
            chunk_a_far_id,
        ]
        assert chunk_b_id not in {result.chunk_id for result in results}
        assert results[0].distance < results[1].distance

        db.execute(
            delete(ChunkEmbedding).where(
                ChunkEmbedding.id.in_(
                    [
                        embedding_a_near_id,
                        embedding_a_far_id,
                        embedding_b_id,
                    ]
                )
            )
        )
        db.execute(
            delete(DocumentChunk).where(
                DocumentChunk.id.in_(
                    [
                        chunk_a_near_id,
                        chunk_a_far_id,
                        chunk_b_id,
                    ]
                )
            )
        )
        db.execute(
            delete(DocumentVersion).where(
                DocumentVersion.id.in_([version_a_id, version_b_id])
            )
        )
        db.execute(
            delete(Document).where(
                Document.id.in_([document_a_id, document_b_id])
            )
        )
        db.execute(
            delete(Organization).where(
                Organization.id.in_([organization_a_id, organization_b_id])
            )
        )
        db.commit()