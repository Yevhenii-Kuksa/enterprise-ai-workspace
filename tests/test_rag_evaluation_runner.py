from app.ai.evaluation.quality_gate import (
    RagQualityGateThresholds,
)
from app.ai.evaluation.runner import (
    build_evaluation_summary,
    run_quality_gate,
)
from app.ai.evaluation.schemas import (
    CitationEvaluationResult,
    EvaluationCaseType,
    GroundednessEvaluationResult,
    RagEvaluationResult,
    ReliabilityEvaluationResult,
    RetrievalEvaluationResult,
    SecurityEvaluationResult,
)
from app.ai.reliability.policy import ReliabilityDecision


def _result(
    *,
    case_id: str = "case-001",
    passed: bool = True,
    hit: bool = True,
    recall_at_k: float = 1.0,
    citation_correctness: float = 1.0,
    citations_passed: bool = True,
    groundedness: float = 1.0,
    groundedness_passed: bool = True,
    reliability_passed: bool = True,
    security_violations: int = 0,
) -> RagEvaluationResult:
    return RagEvaluationResult(
        case_id=case_id,
        case_type=EvaluationCaseType.GROUNDED_ANSWER,
        retrieval=RetrievalEvaluationResult(
            hit=hit,
            expected_evidence_count=1,
            retrieved_expected_evidence_count=(
                1 if hit else 0
            ),
            recall_at_k=recall_at_k,
        ),
        citations=CitationEvaluationResult(
            citation_count=1,
            invalid_citation_count=(
                0 if citations_passed else 1
            ),
            citation_correctness=citation_correctness,
            passed=citations_passed,
        ),
        groundedness=GroundednessEvaluationResult(
            claim_count=1,
            grounded_claim_count=(
                1 if groundedness_passed else 0
            ),
            groundedness=groundedness,
            passed=groundedness_passed,
        ),
        reliability=ReliabilityEvaluationResult(
            expected_decision=ReliabilityDecision.ALLOW,
            actual_decision=ReliabilityDecision.ALLOW,
            passed=reliability_passed,
        ),
        security=SecurityEvaluationResult(
            passed=security_violations == 0,
            violation_count=security_violations,
            reasons=(
                []
                if security_violations == 0
                else ["security_regression"]
            ),
        ),
        passed=passed,
    )


def test_build_evaluation_summary_for_successful_run() -> None:
    results = [
        _result(case_id="case-001"),
        _result(case_id="case-002"),
    ]

    summary = build_evaluation_summary(results)

    assert summary.total_cases == 2
    assert summary.passed_cases == 2
    assert summary.failed_cases == 0
    assert summary.retrieval_hit_rate == 1.0
    assert summary.retrieval_recall_at_k == 1.0
    assert summary.citation_correctness == 1.0
    assert summary.groundedness == 1.0
    assert summary.reliability_accuracy == 1.0
    assert summary.security_violations == 0
    assert summary.passed is False


def test_build_evaluation_summary_aggregates_metrics() -> None:
    results = [
        _result(
            case_id="case-001",
        ),
        _result(
            case_id="case-002",
            passed=False,
            hit=False,
            recall_at_k=0.0,
            citation_correctness=0.5,
            citations_passed=False,
            groundedness=0.5,
            groundedness_passed=False,
            reliability_passed=False,
            security_violations=1,
        ),
    ]

    summary = build_evaluation_summary(results)

    assert summary.total_cases == 2
    assert summary.passed_cases == 1
    assert summary.failed_cases == 1
    assert summary.retrieval_hit_rate == 0.5
    assert summary.retrieval_recall_at_k == 0.5
    assert summary.citation_correctness == 0.75
    assert summary.groundedness == 0.75
    assert summary.reliability_accuracy == 0.5
    assert summary.security_violations == 1


def test_build_evaluation_summary_handles_empty_run() -> None:
    summary = build_evaluation_summary([])

    assert summary.total_cases == 0
    assert summary.passed_cases == 0
    assert summary.failed_cases == 0
    assert summary.retrieval_hit_rate == 0.0
    assert summary.retrieval_recall_at_k == 0.0
    assert summary.citation_correctness == 0.0
    assert summary.groundedness == 0.0
    assert summary.reliability_accuracy == 0.0
    assert summary.security_violations == 0
    assert summary.passed is False


def test_run_quality_gate_passes_successful_run() -> None:
    results = [
        _result(case_id="case-001"),
        _result(case_id="case-002"),
    ]

    summary, gate = run_quality_gate(results)

    assert gate.passed is True
    assert gate.reasons == []
    assert summary.passed is True


def test_run_quality_gate_fails_groundedness_regression() -> None:
    results = [
        _result(case_id="case-001"),
        _result(
            case_id="case-002",
            passed=False,
            groundedness=0.5,
            groundedness_passed=False,
        ),
    ]

    summary, gate = run_quality_gate(results)

    assert summary.groundedness == 0.75
    assert gate.passed is False
    assert summary.passed is False
    assert "groundedness_below_threshold" in gate.reasons


def test_run_quality_gate_fails_security_regression() -> None:
    results = [
        _result(case_id="case-001"),
        _result(
            case_id="case-002",
            passed=False,
            security_violations=1,
        ),
    ]

    summary, gate = run_quality_gate(results)

    assert gate.passed is False
    assert summary.passed is False
    assert "security_violations_above_threshold" in gate.reasons


def test_run_quality_gate_supports_custom_thresholds() -> None:
    results = [
        _result(case_id="case-001"),
        _result(
            case_id="case-002",
            passed=False,
            hit=False,
            recall_at_k=0.5,
            citation_correctness=0.8,
            citations_passed=False,
            groundedness=0.8,
            groundedness_passed=False,
            reliability_passed=False,
        ),
    ]

    thresholds = RagQualityGateThresholds(
        minimum_hit_rate=0.5,
        minimum_recall_at_k=0.75,
        minimum_citation_correctness=0.95,
        minimum_groundedness=0.85,
        minimum_reliability_accuracy=0.5,
        maximum_security_violations=0,
    )

    summary, gate = run_quality_gate(
        results,
        thresholds=thresholds,
    )

    assert summary.retrieval_hit_rate == 0.5
    assert summary.retrieval_recall_at_k == 0.75
    assert summary.citation_correctness == 0.9
    assert summary.groundedness == 0.9
    assert summary.reliability_accuracy == 0.5

    assert gate.passed is False
    assert summary.passed is False
    assert gate.reasons == [
        "citation_correctness_below_threshold",
    ]