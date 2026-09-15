import uuid
from datetime import UTC, datetime, timedelta

from app.ai.reliability.conflict import ConflictStatus
from app.ai.reliability.freshness import FreshnessStatus
from app.ai.reliability.service import evaluate_reliability
from app.ai.reliability.sufficiency import SufficiencyStatus
from app.retrieval.context import build_rag_context
from app.retrieval.evidence import EvidenceItem, build_citation_sources

EVALUATED_AT = datetime(
    2026,
    9,
    15,
    12,
    0,
    tzinfo=UTC,
)


def _build_evidence(
    *,
    distance: float,
    source_modified_at: datetime | None,
) -> EvidenceItem:
    return EvidenceItem(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        document_version_id=uuid.uuid4(),
        document_title="Procedura magazynowa",
        content="Treść fragmentu dokumentu.",
        chunk_index=0,
        distance=distance,
        page_number=1,
        section_title="Magazyn",
        source_locator={"page": 1},
        source_system="sharepoint",
        source_uri="https://example.test/procedura-magazynowa",
        source_modified_at=source_modified_at,
    )


def test_reliability_evaluates_all_gates_from_rag_context() -> None:
    evidence = [
        _build_evidence(
            distance=0.12,
            source_modified_at=EVALUATED_AT - timedelta(days=5),
        ),
        _build_evidence(
            distance=0.55,
            source_modified_at=EVALUATED_AT - timedelta(days=10),
        ),
    ]

    context = build_rag_context(
        query="Jaka jest procedura magazynowa?",
        sources=build_citation_sources(evidence),
    )

    result = evaluate_reliability(
        context=context,
        evaluated_at=EVALUATED_AT,
        max_evidence_distance=0.35,
        max_source_age=timedelta(days=30),
        conflict_count=0,
        conflict_checked=True,
    )

    assert result.sufficiency.status is SufficiencyStatus.SUFFICIENT
    assert result.sufficiency.evidence_count == 2
    assert result.sufficiency.qualifying_evidence_count == 1

    assert result.freshness.status is FreshnessStatus.FRESH
    assert result.freshness.source_count == 2
    assert result.freshness.fresh_source_count == 2

    assert result.conflict.status is ConflictStatus.NONE
    assert result.conflict.conflict_count == 0
    assert result.conflict.checked is True


def test_reliability_preserves_unknown_signals() -> None:
    evidence = [
        _build_evidence(
            distance=0.60,
            source_modified_at=None,
        )
    ]

    context = build_rag_context(
        query="Jaka jest procedura magazynowa?",
        sources=build_citation_sources(evidence),
    )

    result = evaluate_reliability(
        context=context,
        evaluated_at=EVALUATED_AT,
        max_evidence_distance=0.35,
        max_source_age=timedelta(days=30),
    )

    assert result.sufficiency.status is SufficiencyStatus.INSUFFICIENT
    assert result.freshness.status is FreshnessStatus.UNKNOWN
    assert result.conflict.status is ConflictStatus.UNKNOWN


def test_reliability_handles_empty_context_sources() -> None:
    context = build_rag_context(
        query="Jaka jest procedura magazynowa?",
        sources=[],
    )

    result = evaluate_reliability(
        context=context,
        evaluated_at=EVALUATED_AT,
        max_evidence_distance=0.35,
        max_source_age=timedelta(days=30),
    )

    assert result.sufficiency.status is SufficiencyStatus.INSUFFICIENT
    assert result.sufficiency.evidence_count == 0

    assert result.freshness.status is FreshnessStatus.FRESH
    assert result.freshness.source_count == 0

    assert result.conflict.status is ConflictStatus.UNKNOWN