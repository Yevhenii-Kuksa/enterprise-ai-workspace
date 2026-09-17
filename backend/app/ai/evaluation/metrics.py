import uuid
from collections.abc import Iterable

from app.ai.evaluation.schemas import (
    CitationEvaluationResult,
    ExpectedEvidence,
    GroundednessEvaluationResult,
    RetrievalEvaluationResult,
)


def _expected_chunk_ids(
    expected_evidence: Iterable[ExpectedEvidence],
) -> set[uuid.UUID]:
    chunk_ids: set[uuid.UUID] = set()

    for evidence in expected_evidence:
        chunk_ids.update(evidence.chunk_ids)

    return chunk_ids


def evaluate_retrieval(
    *,
    expected_evidence: list[ExpectedEvidence],
    retrieved_chunk_ids: Iterable[uuid.UUID],
) -> RetrievalEvaluationResult:
    expected_chunk_ids = _expected_chunk_ids(expected_evidence)
    retrieved_ids = set(retrieved_chunk_ids)

    if not expected_chunk_ids:
        return RetrievalEvaluationResult(
            hit=True,
            expected_evidence_count=0,
            retrieved_expected_evidence_count=0,
            recall_at_k=1.0,
        )

    retrieved_expected_ids = (
        expected_chunk_ids & retrieved_ids
    )

    expected_count = len(expected_chunk_ids)
    retrieved_expected_count = len(
        retrieved_expected_ids
    )

    return RetrievalEvaluationResult(
        hit=retrieved_expected_count > 0,
        expected_evidence_count=expected_count,
        retrieved_expected_evidence_count=(
            retrieved_expected_count
        ),
        recall_at_k=(
            retrieved_expected_count / expected_count
        ),
    )


def calculate_hit_rate(
    results: Iterable[RetrievalEvaluationResult],
) -> float:
    result_list = list(results)

    if not result_list:
        return 0.0

    hit_count = sum(
        1
        for result in result_list
        if result.hit
    )

    return hit_count / len(result_list)


def calculate_mean_recall_at_k(
    results: Iterable[RetrievalEvaluationResult],
) -> float:
    result_list = list(results)

    if not result_list:
        return 0.0

    return sum(
        result.recall_at_k
        for result in result_list
    ) / len(result_list)


def evaluate_citations(
    *,
    citation_count: int,
    invalid_citation_count: int,
    require_citations: bool,
) -> CitationEvaluationResult:
    if citation_count < 0:
        raise ValueError(
            "Citation count must not be negative."
        )

    if invalid_citation_count < 0:
        raise ValueError(
            "Invalid citation count must not be negative."
        )

    if invalid_citation_count > citation_count:
        raise ValueError(
            "Invalid citation count must not exceed citation count."
        )

    if citation_count == 0:
        correctness = 1.0 if not require_citations else 0.0
    else:
        correctness = (
            citation_count - invalid_citation_count
        ) / citation_count

    passed = (
        invalid_citation_count == 0
        and (
            citation_count > 0
            or not require_citations
        )
    )

    return CitationEvaluationResult(
        citation_count=citation_count,
        invalid_citation_count=invalid_citation_count,
        citation_correctness=correctness,
        passed=passed,
    )

def evaluate_groundedness(
    *,
    claim_count: int,
    grounded_claim_count: int,
) -> GroundednessEvaluationResult:
    if claim_count < 0:
        raise ValueError(
            "Claim count must not be negative."
        )

    if grounded_claim_count < 0:
        raise ValueError(
            "Grounded claim count must not be negative."
        )

    if grounded_claim_count > claim_count:
        raise ValueError(
            "Grounded claim count must not exceed claim count."
        )

    if claim_count == 0:
        groundedness = 1.0
    else:
        groundedness = grounded_claim_count / claim_count

    return GroundednessEvaluationResult(
        claim_count=claim_count,
        grounded_claim_count=grounded_claim_count,
        groundedness=groundedness,
        passed=groundedness == 1.0,
    )