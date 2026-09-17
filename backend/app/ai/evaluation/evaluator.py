import uuid
from collections.abc import Iterable

from app.ai.evaluation.metrics import (
    evaluate_citations,
    evaluate_groundedness,
    evaluate_retrieval,
)
from app.ai.evaluation.schemas import (
    CitationEvaluationResult,
    GroundednessEvaluationResult,
    RagEvaluationCase,
    RagEvaluationResult,
    ReliabilityEvaluationResult,
    RetrievalEvaluationResult,
    SecurityEvaluationResult,
)
from app.ai.reliability.policy import ReliabilityDecision


def evaluate_reliability(
    *,
    expected_decision: ReliabilityDecision | None,
    actual_decision: ReliabilityDecision | None,
) -> ReliabilityEvaluationResult:
    passed = (
        expected_decision is None
        or expected_decision == actual_decision
    )

    return ReliabilityEvaluationResult(
        expected_decision=expected_decision,
        actual_decision=actual_decision,
        passed=passed,
    )


def evaluate_security(
    *,
    security_case: bool,
    violation_reasons: Iterable[str] = (),
) -> SecurityEvaluationResult:
    reasons = [
        reason.strip()
        for reason in violation_reasons
        if reason.strip()
    ]

    if not security_case:
        return SecurityEvaluationResult(
            passed=True,
            violation_count=0,
            reasons=[],
        )

    return SecurityEvaluationResult(
        passed=not reasons,
        violation_count=len(reasons),
        reasons=reasons,
    )


def evaluate_rag_case(
    *,
    case: RagEvaluationCase,
    retrieved_chunk_ids: Iterable[uuid.UUID],
    citation_count: int,
    invalid_citation_count: int,
    claim_count: int,
    grounded_claim_count: int,
    actual_reliability_decision: ReliabilityDecision | None,
    security_violation_reasons: Iterable[str] = (),
) -> RagEvaluationResult:
    retrieval: RetrievalEvaluationResult = evaluate_retrieval(
        expected_evidence=case.expected_evidence,
        retrieved_chunk_ids=retrieved_chunk_ids,
    )

    citations: CitationEvaluationResult = evaluate_citations(
        citation_count=citation_count,
        invalid_citation_count=invalid_citation_count,
        require_citations=case.require_citations,
    )

    groundedness: GroundednessEvaluationResult = (
        evaluate_groundedness(
            claim_count=claim_count,
            grounded_claim_count=grounded_claim_count,
        )
    )

    reliability = evaluate_reliability(
        expected_decision=case.expected_reliability_decision,
        actual_decision=actual_reliability_decision,
    )

    security = evaluate_security(
        security_case=case.security_case,
        violation_reasons=security_violation_reasons,
    )

    passed = all(
        (
            retrieval.recall_at_k == 1.0,
            citations.passed,
            groundedness.passed,
            reliability.passed,
            security.passed,
        )
    )

    return RagEvaluationResult(
        case_id=case.case_id,
        case_type=case.case_type,
        retrieval=retrieval,
        citations=citations,
        groundedness=groundedness,
        reliability=reliability,
        security=security,
        passed=passed,
    )