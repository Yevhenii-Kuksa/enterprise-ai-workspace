import uuid
from datetime import UTC, datetime
from unittest.mock import patch

from app.ai.answer_service import GeneratedAnswer
from app.ai.citation_validation import CitationValidationResult
from app.ai.rag_service import RagAnswerResult
from app.ai.reliability.conflict import (
    ConflictResult,
    ConflictStatus,
)
from app.ai.reliability.freshness import (
    FreshnessResult,
    FreshnessStatus,
)
from app.ai.reliability.policy import (
    ReliabilityDecision,
    ReliabilityPolicyResult,
)
from app.ai.reliability.service import ReliabilityResult
from app.ai.reliability.sufficiency import (
    SufficiencyResult,
    SufficiencyStatus,
)
from app.core.config import Settings, get_settings
from app.db.dependencies import get_db
from app.main import app
from app.retrieval.context import RagContext
from app.retrieval.evidence import CitationSource, EvidenceItem
from app.security.current_user import CurrentUser
from app.security.dependencies import get_current_user
from fastapi.testclient import TestClient


def _current_user() -> CurrentUser:
    return CurrentUser(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        department_id=uuid.uuid4(),
        is_active=True,
        permissions=set(),
    )


def _context() -> RagContext:
    evidence = EvidenceItem(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        document_version_id=uuid.uuid4(),
        document_title="Procedura magazynowa",
        content="Treść procedury magazynowej.",
        chunk_index=0,
        distance=0.1,
        page_number=3,
        section_title="Przyjęcie towaru",
        source_locator={"page": 3},
        source_system="sharepoint",
        source_uri="https://example.test/procedura",
        source_modified_at=datetime(
            2026,
            9,
            10,
            12,
            0,
            tzinfo=UTC,
        ),
    )

    return RagContext(
        query="Jak przyjąć towar?",
        sources=[
            CitationSource(
                label="S1",
                evidence=evidence,
            )
        ],
        context_text="Context",
    )


def _rag_result() -> RagAnswerResult:
    reliability = ReliabilityResult(
        sufficiency=SufficiencyResult(
            status=SufficiencyStatus.SUFFICIENT,
            evidence_count=1,
            qualifying_evidence_count=1,
        ),
        freshness=FreshnessResult(
            status=FreshnessStatus.FRESH,
            source_count=1,
            fresh_source_count=1,
            stale_source_count=0,
            unknown_source_count=0,
        ),
        conflict=ConflictResult(
            status=ConflictStatus.NONE,
            conflict_count=0,
            checked=True,
        ),
    )

    policy = ReliabilityPolicyResult(
        decision=ReliabilityDecision.ALLOW,
        reasons=(),
    )

    answer = GeneratedAnswer(
        text="Towar należy przyjąć zgodnie z procedurą [S1].",
        model_name="fake-answer-model",
        citation_validation=CitationValidationResult(
            used_labels={"S1"},
            valid_labels={"S1"},
            invalid_labels=set(),
            citation_count=1,
            invalid_citation_count=0,
        ),
        reliability=reliability,
        reliability_policy=policy,
    )

    return RagAnswerResult(
        context=_context(),
        answer=answer,
    )


def _override_db() -> object:
    return object()


def _override_settings() -> Settings:
    return Settings(
        database_url="postgresql://test",
        openai_api_key="test-api-key",
    )


def test_rag_query_returns_grounded_answer_contract() -> None:
    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _current_user
    app.dependency_overrides[get_settings] = _override_settings

    try:
        with patch(
            "app.api.rag.answer_rag_query_from_settings",
            return_value=_rag_result(),
        ):
            client = TestClient(app)

            response = client.post(
                "/api/rag/query",
                json={
                    "query": "Jak przyjąć towar?",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    assert response.json() == {
        "answer": "Towar należy przyjąć zgodnie z procedurą [S1].",
        "model_name": "fake-answer-model",
        "citations": [
            {
                "label": "S1",
                "document_title": "Procedura magazynowa",
                "page_number": 3,
                "section_title": "Przyjęcie towaru",
                "source_system": "sharepoint",
                "source_uri": "https://example.test/procedura",
            }
        ],
        "reliability": {
            "decision": "allow",
            "reasons": [],
        },
    }


def test_rag_query_maps_reliability_refusal_to_422() -> None:
    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _current_user
    app.dependency_overrides[get_settings] = _override_settings

    try:
        with patch(
            "app.api.rag.answer_rag_query_from_settings",
            side_effect=ValueError(
                "Reliability policy refused answer generation: "
                "insufficient_evidence"
            ),
        ):
            client = TestClient(app)

            response = client.post(
                "/api/rag/query",
                json={
                    "query": "Pytanie bez wystarczających źródeł",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json() == {
        "detail": (
            "Reliability policy refused answer generation: "
            "insufficient_evidence"
        )
    }


def test_rag_query_rejects_empty_query() -> None:
    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _current_user
    app.dependency_overrides[get_settings] = _override_settings

    try:
        client = TestClient(app)

        response = client.post(
            "/api/rag/query",
            json={
                "query": "",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422