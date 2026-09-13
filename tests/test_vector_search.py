import uuid

from app.db.session import SessionLocal
from app.models.chunk_embedding import ChunkEmbedding
from app.models.department import Department
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_version import DocumentVersion
from app.models.organization import Organization
from app.retrieval.vector_search import search_similar_chunks
from app.security.current_user import CurrentUser
from sqlalchemy import delete


def test_vector_search_ranks_isolates_and_returns_provenance() -> None:
    organization_a_id = uuid.uuid4()
    organization_b_id = uuid.uuid4()

    department_a_id = uuid.uuid4()
    department_b_id = uuid.uuid4()

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

    current_user = CurrentUser(
        id=uuid.uuid4(),
        organization_id=organization_a_id,
        department_id=department_a_id,
        is_active=True,
        permissions=set(),
    )

    with SessionLocal() as db:
        db.add_all(
            [
                Organization(
                    id=organization_a_id,
                    code=f"VECTOR-A-{organization_a_id.hex[:8]}",
                    name="Vector Search Organization A",
                ),
                Organization(
                    id=organization_b_id,
                    code=f"VECTOR-B-{organization_b_id.hex[:8]}",
                    name="Vector Search Organization B",
                ),
                Department(
                    id=department_a_id,
                    organization_id=organization_a_id,
                    code=f"DEPT-A-{department_a_id.hex[:8]}",
                    name="Department A",
                ),
                Department(
                    id=department_b_id,
                    organization_id=organization_b_id,
                    code=f"DEPT-B-{department_b_id.hex[:8]}",
                    name="Department B",
                ),
                Document(
                    id=document_a_id,
                    organization_id=organization_a_id,
                    department_id=department_a_id,
                    title="Procedura magazynowa",
                    source_type="sharepoint",
                    source_system="sharepoint",
                    external_id="document-a",
                ),
                Document(
                    id=document_b_id,
                    organization_id=organization_b_id,
                    department_id=department_b_id,
                    title="Foreign document",
                    source_type="upload",
                    source_system="foreign-system",
                    external_id="document-b",
                ),
                DocumentVersion(
                    id=version_a_id,
                    organization_id=organization_a_id,
                    document_id=document_a_id,
                    version_number=1,
                    content_sha256="a" * 64,
                    source_uri="https://example.test/procedura-magazynowa",
                    ingestion_status="completed",
                ),
                DocumentVersion(
                    id=version_b_id,
                    organization_id=organization_b_id,
                    document_id=document_b_id,
                    version_number=1,
                    content_sha256="b" * 64,
                    source_uri="https://example.test/foreign-document",
                    ingestion_status="completed",
                ),
                DocumentChunk(
                    id=chunk_a_near_id,
                    organization_id=organization_a_id,
                    document_version_id=version_a_id,
                    chunk_index=0,
                    content="Najbardziej trafny fragment",
                    content_sha256="c" * 64,
                    page_number=3,
                    section_title="Magazyn",
                    source_locator={
                        "page": 3,
                        "paragraph": 2,
                    },
                ),
                DocumentChunk(
                    id=chunk_a_far_id,
                    organization_id=organization_a_id,
                    document_version_id=version_a_id,
                    chunk_index=1,
                    content="Mniej trafny fragment",
                    content_sha256="d" * 64,
                    page_number=4,
                    section_title="Logistyka",
                    source_locator={
                        "page": 4,
                    },
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
            current_user=current_user,
            query_embedding=query_embedding,
            embedding_model="test-model",
            limit=10,
        )

        assert [result.chunk_id for result in results] == [
            chunk_a_near_id,
            chunk_a_far_id,
        ]

        assert chunk_b_id not in {
            result.chunk_id
            for result in results
        }

        assert results[0].distance < results[1].distance

        first_result = results[0]

        assert first_result.document_id == document_a_id
        assert first_result.document_version_id == version_a_id
        assert first_result.document_title == "Procedura magazynowa"
        assert first_result.content == "Najbardziej trafny fragment"
        assert first_result.chunk_index == 0
        assert first_result.page_number == 3
        assert first_result.section_title == "Magazyn"
        assert first_result.source_locator == {
            "page": 3,
            "paragraph": 2,
        }
        assert first_result.source_system == "sharepoint"
        assert (
            first_result.source_uri
            == "https://example.test/procedura-magazynowa"
        )

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
                DocumentVersion.id.in_(
                    [
                        version_a_id,
                        version_b_id,
                    ]
                )
            )
        )
        db.execute(
            delete(Document).where(
                Document.id.in_(
                    [
                        document_a_id,
                        document_b_id,
                    ]
                )
            )
        )
        db.execute(
            delete(Department).where(
                Department.id.in_(
                    [
                        department_a_id,
                        department_b_id,
                    ]
                )
            )
        )
        db.execute(
            delete(Organization).where(
                Organization.id.in_(
                    [
                        organization_a_id,
                        organization_b_id,
                    ]
                )
            )
        )
        db.commit()


def test_vector_search_rejects_non_positive_limit() -> None:
    current_user = CurrentUser(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        department_id=None,
        is_active=True,
        permissions=set(),
    )

    with SessionLocal() as db:
        try:
            search_similar_chunks(
                db,
                current_user=current_user,
                query_embedding=[0.0] * 1536,
                embedding_model="test-model",
                limit=0,
            )
        except ValueError as exc:
            assert str(exc) == "Search limit must be greater than zero."
        else:
            raise AssertionError("Expected ValueError.")

def test_vector_search_filters_documents_by_department_access() -> None:
    organization_id = uuid.uuid4()
    department_a_id = uuid.uuid4()
    department_b_id = uuid.uuid4()

    public_document_id = uuid.uuid4()
    own_document_id = uuid.uuid4()
    foreign_department_document_id = uuid.uuid4()

    public_version_id = uuid.uuid4()
    own_version_id = uuid.uuid4()
    foreign_department_version_id = uuid.uuid4()

    public_chunk_id = uuid.uuid4()
    own_chunk_id = uuid.uuid4()
    foreign_department_chunk_id = uuid.uuid4()

    public_embedding_id = uuid.uuid4()
    own_embedding_id = uuid.uuid4()
    foreign_department_embedding_id = uuid.uuid4()

    query_embedding = [1.0, 0.0, 0.0] + [0.0] * 1533
    public_embedding = [0.95, 0.05, 0.0] + [0.0] * 1533
    own_embedding = [0.90, 0.10, 0.0] + [0.0] * 1533
    foreign_department_embedding = [1.0, 0.0, 0.0] + [0.0] * 1533

    current_user = CurrentUser(
        id=uuid.uuid4(),
        organization_id=organization_id,
        department_id=department_a_id,
        is_active=True,
        permissions=set(),
    )

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"VECTOR-DEPT-{organization_id.hex[:8]}",
                name="Vector Department Test",
            )
        )

        db.add_all(
            [
                Department(
                    id=department_a_id,
                    organization_id=organization_id,
                    code=f"DEPT-A-{department_a_id.hex[:8]}",
                    name="Department A",
                ),
                Department(
                    id=department_b_id,
                    organization_id=organization_id,
                    code=f"DEPT-B-{department_b_id.hex[:8]}",
                    name="Department B",
                ),
            ]
        )

        db.add_all(
            [
                Document(
                    id=public_document_id,
                    organization_id=organization_id,
                    department_id=None,
                    title="Public document",
                    source_type="upload",
                ),
                Document(
                    id=own_document_id,
                    organization_id=organization_id,
                    department_id=department_a_id,
                    title="Own department document",
                    source_type="upload",
                ),
                Document(
                    id=foreign_department_document_id,
                    organization_id=organization_id,
                    department_id=department_b_id,
                    title="Foreign department document",
                    source_type="upload",
                ),
            ]
        )

        db.add_all(
            [
                DocumentVersion(
                    id=public_version_id,
                    organization_id=organization_id,
                    document_id=public_document_id,
                    version_number=1,
                    content_sha256="a" * 64,
                    ingestion_status="completed",
                ),
                DocumentVersion(
                    id=own_version_id,
                    organization_id=organization_id,
                    document_id=own_document_id,
                    version_number=1,
                    content_sha256="b" * 64,
                    ingestion_status="completed",
                ),
                DocumentVersion(
                    id=foreign_department_version_id,
                    organization_id=organization_id,
                    document_id=foreign_department_document_id,
                    version_number=1,
                    content_sha256="c" * 64,
                    ingestion_status="completed",
                ),
            ]
        )

        db.add_all(
            [
                DocumentChunk(
                    id=public_chunk_id,
                    organization_id=organization_id,
                    document_version_id=public_version_id,
                    chunk_index=0,
                    content="Public chunk",
                    content_sha256="d" * 64,
                ),
                DocumentChunk(
                    id=own_chunk_id,
                    organization_id=organization_id,
                    document_version_id=own_version_id,
                    chunk_index=0,
                    content="Own department chunk",
                    content_sha256="e" * 64,
                ),
                DocumentChunk(
                    id=foreign_department_chunk_id,
                    organization_id=organization_id,
                    document_version_id=foreign_department_version_id,
                    chunk_index=0,
                    content="Foreign department chunk",
                    content_sha256="f" * 64,
                ),
            ]
        )

        db.add_all(
            [
                ChunkEmbedding(
                    id=public_embedding_id,
                    organization_id=organization_id,
                    document_chunk_id=public_chunk_id,
                    embedding_model="test-model",
                    dimensions=1536,
                    embedding=public_embedding,
                ),
                ChunkEmbedding(
                    id=own_embedding_id,
                    organization_id=organization_id,
                    document_chunk_id=own_chunk_id,
                    embedding_model="test-model",
                    dimensions=1536,
                    embedding=own_embedding,
                ),
                ChunkEmbedding(
                    id=foreign_department_embedding_id,
                    organization_id=organization_id,
                    document_chunk_id=foreign_department_chunk_id,
                    embedding_model="test-model",
                    dimensions=1536,
                    embedding=foreign_department_embedding,
                ),
            ]
        )

        db.commit()

        results = search_similar_chunks(
            db,
            current_user=current_user,
            query_embedding=query_embedding,
            embedding_model="test-model",
            limit=10,
        )

        result_chunk_ids = {
            result.chunk_id
            for result in results
        }

        assert public_chunk_id in result_chunk_ids
        assert own_chunk_id in result_chunk_ids
        assert foreign_department_chunk_id not in result_chunk_ids

        db.execute(
            delete(ChunkEmbedding).where(
                ChunkEmbedding.id.in_(
                    [
                        public_embedding_id,
                        own_embedding_id,
                        foreign_department_embedding_id,
                    ]
                )
            )
        )
        db.execute(
            delete(DocumentChunk).where(
                DocumentChunk.id.in_(
                    [
                        public_chunk_id,
                        own_chunk_id,
                        foreign_department_chunk_id,
                    ]
                )
            )
        )
        db.execute(
            delete(DocumentVersion).where(
                DocumentVersion.id.in_(
                    [
                        public_version_id,
                        own_version_id,
                        foreign_department_version_id,
                    ]
                )
            )
        )
        db.execute(
            delete(Document).where(
                Document.id.in_(
                    [
                        public_document_id,
                        own_document_id,
                        foreign_department_document_id,
                    ]
                )
            )
        )
        db.execute(
            delete(Department).where(
                Department.id.in_(
                    [
                        department_a_id,
                        department_b_id,
                    ]
                )
            )
        )
        db.execute(
            delete(Organization).where(
                Organization.id == organization_id
            )
        )
        db.commit()

def test_vector_search_rejects_inactive_user() -> None:
    current_user = CurrentUser(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        department_id=None,
        is_active=False,
        permissions=set(),
    )

    with SessionLocal() as db:
        try:
            search_similar_chunks(
                db,
                current_user=current_user,
                query_embedding=[0.0] * 1536,
                embedding_model="test-model",
                limit=10,
            )
        except PermissionError as exc:
            assert str(exc) == (
                "Inactive user cannot perform vector search."
            )
        else:
            raise AssertionError("Expected PermissionError.")