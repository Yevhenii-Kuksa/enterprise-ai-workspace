import uuid

import pytest
from app.ai.evaluation.metrics import (
    calculate_hit_rate,
    calculate_mean_recall_at_k,
    evaluate_citations,
    evaluate_groundedness,
    evaluate_retrieval,
)
from app.ai.evaluation.schemas import (
    ExpectedEvidence,
    RetrievalEvaluationResult,
)


def test_evaluate_retrieval_returns_full_match() -> None:
    chunk_a = uuid.uuid4()
    chunk_b = uuid.uuid4()

    result = evaluate_retrieval(
        expected_evidence=[
            ExpectedEvidence(
                document_id=uuid.uuid4(),
                chunk_ids={chunk_a, chunk_b},
            )
        ],
        retrieved_chunk_ids=[
            chunk_a,
            chunk_b,
        ],
    )

    assert result.hit is True
    assert result.expected_evidence_count == 2
    assert result.retrieved_expected_evidence_count == 2
    assert result.recall_at_k == 1.0


def test_evaluate_retrieval_returns_partial_match() -> None:
    chunk_a = uuid.uuid4()
    chunk_b = uuid.uuid4()

    result = evaluate_retrieval(
        expected_evidence=[
            ExpectedEvidence(
                document_id=uuid.uuid4(),
                chunk_ids={chunk_a, chunk_b},
            )
        ],
        retrieved_chunk_ids=[
            chunk_a,
            uuid.uuid4(),
        ],
    )

    assert result.hit is True
    assert result.expected_evidence_count == 2
    assert result.retrieved_expected_evidence_count == 1
    assert result.recall_at_k == 0.5


def test_evaluate_retrieval_returns_miss() -> None:
    result = evaluate_retrieval(
        expected_evidence=[
            ExpectedEvidence(
                document_id=uuid.uuid4(),
                chunk_ids={
                    uuid.uuid4(),
                },
            )
        ],
        retrieved_chunk_ids=[
            uuid.uuid4(),
        ],
    )

    assert result.hit is False
    assert result.retrieved_expected_evidence_count == 0
    assert result.recall_at_k == 0.0


def test_evaluate_retrieval_without_expected_chunks_passes() -> None:
    result = evaluate_retrieval(
        expected_evidence=[],
        retrieved_chunk_ids=[],
    )

    assert result.hit is True
    assert result.expected_evidence_count == 0
    assert result.retrieved_expected_evidence_count == 0
    assert result.recall_at_k == 1.0


def test_calculate_hit_rate() -> None:
    results = [
        RetrievalEvaluationResult(
            hit=True,
            expected_evidence_count=1,
            retrieved_expected_evidence_count=1,
            recall_at_k=1.0,
        ),
        RetrievalEvaluationResult(
            hit=False,
            expected_evidence_count=1,
            retrieved_expected_evidence_count=0,
            recall_at_k=0.0,
        ),
        RetrievalEvaluationResult(
            hit=True,
            expected_evidence_count=2,
            retrieved_expected_evidence_count=1,
            recall_at_k=0.5,
        ),
    ]

    assert calculate_hit_rate(results) == pytest.approx(
        2 / 3
    )


def test_calculate_mean_recall_at_k() -> None:
    results = [
        RetrievalEvaluationResult(
            hit=True,
            expected_evidence_count=1,
            retrieved_expected_evidence_count=1,
            recall_at_k=1.0,
        ),
        RetrievalEvaluationResult(
            hit=True,
            expected_evidence_count=2,
            retrieved_expected_evidence_count=1,
            recall_at_k=0.5,
        ),
    ]

    assert calculate_mean_recall_at_k(
        results
    ) == pytest.approx(0.75)


def test_empty_metric_collections_return_zero() -> None:
    assert calculate_hit_rate([]) == 0.0
    assert calculate_mean_recall_at_k([]) == 0.0


def test_evaluate_citations_passes_valid_citations() -> None:
    result = evaluate_citations(
        citation_count=3,
        invalid_citation_count=0,
        require_citations=True,
    )

    assert result.passed is True
    assert result.citation_correctness == 1.0


def test_evaluate_citations_detects_invalid_citations() -> None:
    result = evaluate_citations(
        citation_count=4,
        invalid_citation_count=1,
        require_citations=True,
    )

    assert result.passed is False
    assert result.citation_correctness == 0.75


def test_evaluate_citations_requires_citation_when_configured() -> None:
    result = evaluate_citations(
        citation_count=0,
        invalid_citation_count=0,
        require_citations=True,
    )

    assert result.passed is False
    assert result.citation_correctness == 0.0


def test_evaluate_citations_allows_no_citations_when_not_required() -> None:
    result = evaluate_citations(
        citation_count=0,
        invalid_citation_count=0,
        require_citations=False,
    )

    assert result.passed is True
    assert result.citation_correctness == 1.0


@pytest.mark.parametrize(
    ("citation_count", "invalid_citation_count"),
    [
        (-1, 0),
        (1, -1),
        (1, 2),
    ],
)
def test_evaluate_citations_rejects_invalid_counts(
    citation_count: int,
    invalid_citation_count: int,
) -> None:
    with pytest.raises(ValueError):
        evaluate_citations(
            citation_count=citation_count,
            invalid_citation_count=invalid_citation_count,
            require_citations=True,
        )

def test_groundedness_passes_when_all_claims_are_grounded() -> None:
    result = evaluate_groundedness(
        claim_count=4,
        grounded_claim_count=4,
    )

    assert result.claim_count == 4
    assert result.grounded_claim_count == 4
    assert result.groundedness == 1.0
    assert result.passed is True


def test_groundedness_fails_when_claim_is_not_grounded() -> None:
    result = evaluate_groundedness(
        claim_count=4,
        grounded_claim_count=3,
    )

    assert result.groundedness == 0.75
    assert result.passed is False


def test_groundedness_handles_no_claims() -> None:
    result = evaluate_groundedness(
        claim_count=0,
        grounded_claim_count=0,
    )

    assert result.groundedness == 1.0
    assert result.passed is True


def test_groundedness_rejects_negative_claim_count() -> None:
    try:
        evaluate_groundedness(
            claim_count=-1,
            grounded_claim_count=0,
        )
    except ValueError as exc:
        assert str(exc) == "Claim count must not be negative."
    else:
        raise AssertionError("Expected ValueError.")


def test_groundedness_rejects_negative_grounded_claim_count() -> None:
    try:
        evaluate_groundedness(
            claim_count=1,
            grounded_claim_count=-1,
        )
    except ValueError as exc:
        assert str(exc) == (
            "Grounded claim count must not be negative."
        )
    else:
        raise AssertionError("Expected ValueError.")


def test_groundedness_rejects_grounded_count_above_claim_count() -> None:
    try:
        evaluate_groundedness(
            claim_count=2,
            grounded_claim_count=3,
        )
    except ValueError as exc:
        assert str(exc) == (
            "Grounded claim count must not exceed claim count."
        )
    else:
        raise AssertionError("Expected ValueError.")