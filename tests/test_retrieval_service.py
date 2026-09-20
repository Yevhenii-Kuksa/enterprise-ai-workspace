import logging
import uuid

from app.core.trace_context import TraceContext
from app.db.session import SessionLocal
from app.models.chunk_embedding import ChunkEmbedding
from app.models.department import Department
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.document_version import DocumentVersion
from app.models.organization import Organization
from app.retrieval.service import prepare_rag_context, retrieve_evidence
from app.security.current_user import CurrentUser


class FakeEmbeddingProvider:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    @property
    def model_name(self) -> str:
        return "fake-model"

    @property
    def dimensions(self) -> int:
        return 1536

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        self.calls.append(texts)

        return [
            [1.0] + [0.0] * 1535
            for _ in texts
        ]


def test_retrieve_evidence_rejects_empty_query() -> None:
    provider = FakeEmbeddingProvider()
    current_user = CurrentUser(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        department_id=None,
        is_active=True,
        permissions=set(),
    )

    with SessionLocal() as db:
        try:
            retrieve_evidence(
                db,
                current_user=current_user,
                query="   ",
                embedding_provider=provider,
            )
        except ValueError as exc:
            assert str(exc) == "Query must not be empty."
        else:
            raise AssertionError("Expected ValueError.")

    assert provider.calls == []


def test_retrieve_evidence_normalizes_query_before_embedding() -> None:
    provider = FakeEmbeddingProvider()
    current_user = CurrentUser(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        department_id=None,
        is_active=True,
        permissions=set(),
    )

    with SessionLocal() as db:
        result = retrieve_evidence(
            db,
            current_user=current_user,
            query="  test query  ",
            embedding_provider=provider,
        )

    assert result.query == "test query"
    assert result.evidence == []
    assert provider.calls == [["test query"]]


def test_retrieve_evidence_returns_empty_evidence_when_no_chunks_match() -> None:
    provider = FakeEmbeddingProvider()
    current_user = CurrentUser(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        department_id=None,
        is_active=True,
        permissions=set(),
    )

    with SessionLocal() as db:
        result = retrieve_evidence(
            db,
            current_user=current_user,
            query="Where is the warehouse procedure?",
            embedding_provider=provider,
            limit=5,
        )

    assert result.query == "Where is the warehouse procedure?"
    assert result.evidence == []
    assert provider.calls == [
        ["Where is the warehouse procedure?"]
    ]


def test_retrieve_evidence_returns_matching_chunk_with_provenance() -> None:
    organization_id = uuid.uuid4()
    document_id = uuid.uuid4()
    document_version_id = uuid.uuid4()
    document_chunk_id = uuid.uuid4()

    provider = FakeEmbeddingProvider()

    current_user = CurrentUser(
        id=uuid.uuid4(),
        organization_id=organization_id,
        department_id=None,
        is_active=True,
        permissions=set(),
    )

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"RETRIEVAL-{organization_id.hex[:8]}",
                name="Retrieval Service Test",
            )
        )
        db.add(
            Document(
                id=document_id,
                organization_id=organization_id,
                department_id=None,
                title="Procedura magazynowa",
                source_type="sharepoint",
                source_system="sharepoint",
                external_id="retrieval-service-document",
            )
        )
        db.add(
            DocumentVersion(
                id=document_version_id,
                organization_id=organization_id,
                document_id=document_id,
                version_number=1,
                content_sha256="a" * 64,
                source_uri="https://example.test/procedura-magazynowa",
                ingestion_status="completed",
            )
        )
        db.add(
            DocumentChunk(
                id=document_chunk_id,
                organization_id=organization_id,
                document_version_id=document_version_id,
                chunk_index=0,
                content="Towar należy przyjąć zgodnie z procedurą magazynową.",
                content_sha256="b" * 64,
                page_number=7,
                section_title="Przyjęcie towaru",
                source_locator={"page": 7},
            )
        )
        db.add(
            ChunkEmbedding(
                organization_id=organization_id,
                document_chunk_id=document_chunk_id,
                embedding_model="fake-model",
                dimensions=1536,
                embedding=[1.0] + [0.0] * 1535,
            )
        )
        db.flush()

        result = retrieve_evidence(
            db,
            current_user=current_user,
            query="Jak przyjąć towar?",
            embedding_provider=provider,
            limit=5,
        )

        assert result.query == "Jak przyjąć towar?"
        assert len(result.evidence) == 1

        evidence = result.evidence[0]

        assert evidence.chunk_id == document_chunk_id
        assert evidence.document_id == document_id
        assert evidence.document_version_id == document_version_id
        assert evidence.document_title == "Procedura magazynowa"
        assert evidence.page_number == 7
        assert evidence.section_title == "Przyjęcie towaru"
        assert evidence.source_locator == {"page": 7}
        assert evidence.source_system == "sharepoint"
        assert (
            evidence.source_uri
            == "https://example.test/procedura-magazynowa"
        )

        assert provider.calls == [["Jak przyjąć towar?"]]

        db.rollback()


def test_retrieve_evidence_does_not_return_foreign_department_chunk() -> None:
    organization_id = uuid.uuid4()
    user_department_id = uuid.uuid4()
    foreign_department_id = uuid.uuid4()

    document_id = uuid.uuid4()
    document_version_id = uuid.uuid4()
    document_chunk_id = uuid.uuid4()

    provider = FakeEmbeddingProvider()

    current_user = CurrentUser(
        id=uuid.uuid4(),
        organization_id=organization_id,
        department_id=user_department_id,
        is_active=True,
        permissions=set(),
    )

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"RETRIEVAL-SEC-{organization_id.hex[:8]}",
                name="Retrieval Security Test",
            )
        )

        db.add_all(
            [
                Department(
                    id=user_department_id,
                    organization_id=organization_id,
                    code=f"USER-{user_department_id.hex[:8]}",
                    name="User Department",
                ),
                Department(
                    id=foreign_department_id,
                    organization_id=organization_id,
                    code=f"FOREIGN-{foreign_department_id.hex[:8]}",
                    name="Foreign Department",
                ),
            ]
        )

        db.add(
            Document(
                id=document_id,
                organization_id=organization_id,
                department_id=foreign_department_id,
                title="Poufny dokument HR",
                source_type="upload",
            )
        )

        db.add(
            DocumentVersion(
                id=document_version_id,
                organization_id=organization_id,
                document_id=document_id,
                version_number=1,
                content_sha256="c" * 64,
                ingestion_status="completed",
            )
        )

        db.add(
            DocumentChunk(
                id=document_chunk_id,
                organization_id=organization_id,
                document_version_id=document_version_id,
                chunk_index=0,
                content="Poufne informacje działu HR.",
                content_sha256="d" * 64,
            )
        )

        db.add(
            ChunkEmbedding(
                organization_id=organization_id,
                document_chunk_id=document_chunk_id,
                embedding_model="fake-model",
                dimensions=1536,
                embedding=[1.0] + [0.0] * 1535,
            )
        )

        db.flush()

        result = retrieve_evidence(
            db,
            current_user=current_user,
            query="Poufne informacje działu HR",
            embedding_provider=provider,
            limit=5,
        )

        assert result.evidence == []
        assert provider.calls == [["Poufne informacje działu HR"]]

        db.rollback()


def test_prepare_rag_context_builds_citation_ready_context() -> None:
    organization_id = uuid.uuid4()
    document_id = uuid.uuid4()
    document_version_id = uuid.uuid4()
    document_chunk_id = uuid.uuid4()

    provider = FakeEmbeddingProvider()

    current_user = CurrentUser(
        id=uuid.uuid4(),
        organization_id=organization_id,
        department_id=None,
        is_active=True,
        permissions=set(),
    )

    with SessionLocal() as db:
        db.add(
            Organization(
                id=organization_id,
                code=f"RAG-{organization_id.hex[:8]}",
                name="RAG Context Test",
            )
        )
        db.add(
            Document(
                id=document_id,
                organization_id=organization_id,
                department_id=None,
                title="Instrukcja jakości",
                source_type="sharepoint",
                source_system="sharepoint",
                external_id="rag-context-document",
            )
        )
        db.add(
            DocumentVersion(
                id=document_version_id,
                organization_id=organization_id,
                document_id=document_id,
                version_number=1,
                content_sha256="e" * 64,
                source_uri="https://example.test/instrukcja-jakosci",
                ingestion_status="completed",
            )
        )
        db.add(
            DocumentChunk(
                id=document_chunk_id,
                organization_id=organization_id,
                document_version_id=document_version_id,
                chunk_index=0,
                content="Kontrola jakości jest wykonywana przed wysyłką.",
                content_sha256="f" * 64,
                page_number=4,
                section_title="Kontrola jakości",
                source_locator={"page": 4},
            )
        )
        db.add(
            ChunkEmbedding(
                organization_id=organization_id,
                document_chunk_id=document_chunk_id,
                embedding_model="fake-model",
                dimensions=1536,
                embedding=[1.0] + [0.0] * 1535,
            )
        )
        db.flush()

        context = prepare_rag_context(
            db,
            current_user=current_user,
            query="  Kiedy wykonywana jest kontrola jakości?  ",
            embedding_provider=provider,
            limit=5,
        )

        assert context.query == "Kiedy wykonywana jest kontrola jakości?"
        assert len(context.sources) == 1
        assert context.sources[0].label == "S1"

        evidence = context.sources[0].evidence

        assert evidence.chunk_id == document_chunk_id
        assert evidence.document_id == document_id
        assert evidence.document_version_id == document_version_id
        assert evidence.document_title == "Instrukcja jakości"
        assert evidence.page_number == 4
        assert evidence.section_title == "Kontrola jakości"
        assert evidence.source_locator == {"page": 4}
        assert evidence.source_system == "sharepoint"
        assert (
            evidence.source_uri
            == "https://example.test/instrukcja-jakosci"
        )

        assert "[S1]" in context.context_text
        assert "Document: Instrukcja jakości" in context.context_text
        assert (
            "Content: Kontrola jakości jest wykonywana przed wysyłką."
            in context.context_text
        )

        assert provider.calls == [
            ["Kiedy wykonywana jest kontrola jakości?"]
        ]

        db.rollback()

def test_retrieve_evidence_emits_correlated_trace(
    caplog,
) -> None:
    provider = FakeEmbeddingProvider()
    current_user = CurrentUser(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        department_id=None,
        is_active=True,
        permissions=set(),
    )

    trace_context = TraceContext.create()

    application_logger = logging.getLogger(
        "enterprise_ai_workspace"
    )
    application_logger.addHandler(caplog.handler)

    try:
        with SessionLocal() as db:
            with caplog.at_level(
                "INFO",
                logger="enterprise_ai_workspace.retrieval",
            ):
                result = retrieve_evidence(
                    db,
                    current_user=current_user,
                    query="Where is the warehouse procedure?",
                    embedding_provider=provider,
                    limit=5,
                    trace_context=trace_context,
                )
    finally:
        application_logger.removeHandler(caplog.handler)

    assert result.evidence == []

    matching_records = [
        record
        for record in caplog.records
        if getattr(record, "event_type", None)
        == "retrieval_completed"
    ]

    assert len(matching_records) == 1

    record = matching_records[0]

    assert record.trace_id == str(trace_context.trace_id)
    assert record.request_id == str(trace_context.request_id)
    assert record.action_id is None
    assert record.organization_id == str(current_user.organization_id)
    assert record.user_id == str(current_user.id)
    assert record.embedding_model == "fake-model"
    assert record.requested_limit == 5
    assert record.evidence_count == 0
    assert record.best_distance is None
    assert isinstance(record.duration_ms, float)
    assert record.duration_ms >= 0

class FailingEmbeddingProvider:
    @property
    def model_name(self) -> str:
        return "fake-failing-model"

    @property
    def dimensions(self) -> int:
        return 1536

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        raise ConnectionError(
            "Synthetic embedding provider failure."
        )


def test_retrieve_evidence_emits_embedding_failure_trace(
    caplog,
) -> None:
    provider = FailingEmbeddingProvider()

    current_user = CurrentUser(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        department_id=None,
        is_active=True,
        permissions=set(),
    )

    trace_context = TraceContext.create()

    application_logger = logging.getLogger(
        "enterprise_ai_workspace"
    )
    application_logger.addHandler(caplog.handler)

    try:
        with SessionLocal() as db:
            with caplog.at_level(
                "ERROR",
                logger="enterprise_ai_workspace.retrieval",
            ):
                try:
                    retrieve_evidence(
                        db,
                        current_user=current_user,
                        query="Where is the warehouse procedure?",
                        embedding_provider=provider,
                        limit=5,
                        trace_context=trace_context,
                    )
                except ConnectionError:
                    pass
    finally:
        application_logger.removeHandler(caplog.handler)

    matching_records = [
        record
        for record in caplog.records
        if getattr(record, "event_type", None)
        == "retrieval_failed"
    ]

    assert len(matching_records) == 1

    record = matching_records[0]

    assert record.trace_id == str(trace_context.trace_id)
    assert record.request_id == str(trace_context.request_id)
    assert record.action_id is None
    assert record.organization_id == str(
        current_user.organization_id
    )
    assert record.user_id == str(current_user.id)
    assert record.requested_limit == 5
    assert record.error_type == "ConnectionError"
    assert record.error_category == "dependency"
    assert isinstance(record.duration_ms, float)
    assert record.duration_ms >= 0

def test_retrieve_evidence_emits_database_failure_trace(
    caplog,
    monkeypatch,
) -> None:
    provider = FakeEmbeddingProvider()

    current_user = CurrentUser(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        department_id=None,
        is_active=True,
        permissions=set(),
    )

    trace_context = TraceContext.create()

    def fail_vector_search(*args, **kwargs):
        raise RuntimeError(
            "Synthetic database failure."
        )

    monkeypatch.setattr(
        "app.retrieval.service.search_similar_chunks",
        fail_vector_search,
    )

    application_logger = logging.getLogger(
        "enterprise_ai_workspace"
    )
    application_logger.addHandler(caplog.handler)

    try:
        with SessionLocal() as db:
            with caplog.at_level(
                "ERROR",
                logger="enterprise_ai_workspace.retrieval",
            ):
                try:
                    retrieve_evidence(
                        db,
                        current_user=current_user,
                        query="Where is the warehouse procedure?",
                        embedding_provider=provider,
                        limit=5,
                        trace_context=trace_context,
                    )
                except RuntimeError:
                    pass
    finally:
        application_logger.removeHandler(caplog.handler)

    matching_records = [
        record
        for record in caplog.records
        if getattr(record, "event_type", None)
        == "retrieval_failed"
    ]

    assert len(matching_records) == 1

    record = matching_records[0]

    assert record.trace_id == str(trace_context.trace_id)
    assert record.request_id == str(trace_context.request_id)
    assert record.action_id is None
    assert record.organization_id == str(
        current_user.organization_id
    )
    assert record.user_id == str(current_user.id)
    assert record.requested_limit == 5
    assert record.error_type == "RuntimeError"
    assert record.error_category == "database"
    assert isinstance(record.duration_ms, float)
    assert record.duration_ms >= 0