import uuid

from app.ai.evaluation.evaluator import (
    evaluate_rag_case,
    evaluate_reliability,
    evaluate_security,
)
from app.ai.evaluation.schemas import (
    EvaluationCaseType,
    ExpectedEvidence,
    RagEvaluationCase,
)
from app.ai.reliability.policy import ReliabilityDecision


def _evaluation_case(
    *,
    chunk_ids: set[uuid.UUID] | None = None,
    expected_decision: ReliabilityDecision | None = (
        ReliabilityDecision.ALLOW
    ),
    require_citations: bool = True,
    security_case: bool = False,
) -> RagEvaluationCase:
    expected_evidence = []

    if chunk_ids is not None:
        expected_evidence = [
            ExpectedEvidence(
                document_id=uuid.uuid4(),
                chunk_ids=chunk_ids,
            )
        ]

    return RagEvaluationCase(
        case_id="case-001",
        case_type=EvaluationCaseType.GROUNDED_ANSWER,
        organization_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        query="Jaka jest procedura reklamacji?",
        expected_evidence=expected_evidence,
        expected_reliability_decision=expected_decision,
        require_citations=require_citations,
        security_case=security_case,
    )


def test_evaluate_reliability_matches_expected_decision() -> None:
    result = evaluate_reliability(
        expected_decision=ReliabilityDecision.ALLOW,
        actual_decision=ReliabilityDecision.ALLOW,
    )

    assert result.passed is True
    assert result.expected_decision == ReliabilityDecision.ALLOW
    assert result.actual_decision == ReliabilityDecision.ALLOW


def test_evaluate_reliability_detects_mismatch() -> None:
    result = evaluate_reliability(
        expected_decision=ReliabilityDecision.REFUSE,
        actual_decision=ReliabilityDecision.ALLOW,
    )

    assert result.passed is False


def test_evaluate_reliability_without_expectation_passes() -> None:
    result = evaluate_reliability(
        expected_decision=None,
        actual_decision=ReliabilityDecision.DEGRADE,
    )

    assert result.passed is True


def test_evaluate_security_passes_non_security_case() -> None:
    result = evaluate_security(
        security_case=False,
        violation_reasons=[
            "ignored for non-security case",
        ],
    )

    assert result.passed is True
    assert result.violation_count == 0
    assert result.reasons == []


def test_evaluate_security_detects_violations() -> None:
    result = evaluate_security(
        security_case=True,
        violation_reasons=[
            "cross_tenant_document",
            " ",
            "unauthorized_source",
        ],
    )

    assert result.passed is False
    assert result.violation_count == 2
    assert result.reasons == [
        "cross_tenant_document",
        "unauthorized_source",
    ]


def test_evaluate_security_passes_without_violations() -> None:
    result = evaluate_security(
        security_case=True,
    )

    assert result.passed is True
    assert result.violation_count == 0


def test_evaluate_rag_case_passes_complete_case() -> None:
    chunk_a = uuid.uuid4()
    chunk_b = uuid.uuid4()

    case = _evaluation_case(
        chunk_ids={chunk_a, chunk_b},
    )

    result = evaluate_rag_case(
        case=case,
        retrieved_chunk_ids=[chunk_a, chunk_b],
        citation_count=2,
        invalid_citation_count=0,
        claim_count=3,
        grounded_claim_count=3,
        actual_reliability_decision=ReliabilityDecision.ALLOW,
    )

    assert result.passed is True

    assert result.retrieval is not None
    assert result.retrieval.recall_at_k == 1.0

    assert result.citations is not None
    assert result.citations.passed is True

    assert result.groundedness is not None
    assert result.groundedness.groundedness == 1.0
    assert result.groundedness.passed is True

    assert result.reliability is not None
    assert result.reliability.passed is True

    assert result.security is not None
    assert result.security.passed is True


def test_evaluate_rag_case_fails_partial_retrieval() -> None:
    chunk_a = uuid.uuid4()
    chunk_b = uuid.uuid4()

    case = _evaluation_case(
        chunk_ids={chunk_a, chunk_b},
    )

    result = evaluate_rag_case(
        case=case,
        retrieved_chunk_ids=[chunk_a],
        citation_count=1,
        invalid_citation_count=0,
        claim_count=2,
        grounded_claim_count=2,
        actual_reliability_decision=ReliabilityDecision.ALLOW,
    )

    assert result.passed is False

    assert result.retrieval is not None
    assert result.retrieval.recall_at_k == 0.5


def test_evaluate_rag_case_fails_invalid_citation() -> None:
    chunk_id = uuid.uuid4()

    case = _evaluation_case(
        chunk_ids={chunk_id},
    )

    result = evaluate_rag_case(
        case=case,
        retrieved_chunk_ids=[chunk_id],
        citation_count=2,
        invalid_citation_count=1,
        claim_count=2,
        grounded_claim_count=2,
        actual_reliability_decision=ReliabilityDecision.ALLOW,
    )

    assert result.passed is False

    assert result.citations is not None
    assert result.citations.passed is False


def test_evaluate_rag_case_fails_ungrounded_claim() -> None:
    chunk_id = uuid.uuid4()

    case = _evaluation_case(
        chunk_ids={chunk_id},
    )

    result = evaluate_rag_case(
        case=case,
        retrieved_chunk_ids=[chunk_id],
        citation_count=1,
        invalid_citation_count=0,
        claim_count=4,
        grounded_claim_count=3,
        actual_reliability_decision=ReliabilityDecision.ALLOW,
    )

    assert result.passed is False

    assert result.groundedness is not None
    assert result.groundedness.groundedness == 0.75
    assert result.groundedness.passed is False


def test_evaluate_rag_case_fails_reliability_mismatch() -> None:
    chunk_id = uuid.uuid4()

    case = _evaluation_case(
        chunk_ids={chunk_id},
        expected_decision=ReliabilityDecision.REFUSE,
    )

    result = evaluate_rag_case(
        case=case,
        retrieved_chunk_ids=[chunk_id],
        citation_count=1,
        invalid_citation_count=0,
        claim_count=1,
        grounded_claim_count=1,
        actual_reliability_decision=ReliabilityDecision.ALLOW,
    )

    assert result.passed is False

    assert result.reliability is not None
    assert result.reliability.passed is False


def test_evaluate_rag_case_fails_security_violation() -> None:
    chunk_id = uuid.uuid4()

    case = _evaluation_case(
        chunk_ids={chunk_id},
        security_case=True,
    )

    result = evaluate_rag_case(
        case=case,
        retrieved_chunk_ids=[chunk_id],
        citation_count=1,
        invalid_citation_count=0,
        claim_count=1,
        grounded_claim_count=1,
        actual_reliability_decision=ReliabilityDecision.ALLOW,
        security_violation_reasons=[
            "cross_tenant_document",
        ],
    )

    assert result.passed is False

    assert result.security is not None
    assert result.security.violation_count == 1