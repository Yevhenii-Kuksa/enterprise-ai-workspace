from collections.abc import Iterable

from app.ai.evaluation.metrics import (
    calculate_hit_rate,
    calculate_mean_recall_at_k,
)
from app.ai.evaluation.quality_gate import (
    RagQualityGateResult,
    RagQualityGateThresholds,
    evaluate_quality_gate,
)
from app.ai.evaluation.schemas import (
    CitationEvaluationResult,
    GroundednessEvaluationResult,
    RagEvaluationResult,
    RagEvaluationSummary,
    ReliabilityEvaluationResult,
    RetrievalEvaluationResult,
    SecurityEvaluationResult,
)


def _mean(values: Iterable[float]) -> float:
    value_list = list(values)

    if not value_list:
        return 0.0

    return sum(value_list) / len(value_list)


def build_evaluation_summary(
    results: list[RagEvaluationResult],
) -> RagEvaluationSummary:
    retrieval_results: list[RetrievalEvaluationResult] = []
    citation_results: list[CitationEvaluationResult] = []
    groundedness_results: list[GroundednessEvaluationResult] = []
    reliability_results: list[ReliabilityEvaluationResult] = []
    security_results: list[SecurityEvaluationResult] = []

    for result in results:
        if result.retrieval is not None:
            retrieval_results.append(result.retrieval)

        if result.citations is not None:
            citation_results.append(result.citations)

        if result.groundedness is not None:
            groundedness_results.append(result.groundedness)

        if result.reliability is not None:
            reliability_results.append(result.reliability)

        if result.security is not None:
            security_results.append(result.security)

    total_cases = len(results)
    passed_cases = sum(
        1
        for result in results
        if result.passed
    )
    failed_cases = total_cases - passed_cases

    citation_correctness = _mean(
        result.citation_correctness
        for result in citation_results
    )

    groundedness = _mean(
        result.groundedness
        for result in groundedness_results
    )

    reliability_accuracy = _mean(
        1.0 if result.passed else 0.0
        for result in reliability_results
    )

    security_violations = sum(
        result.violation_count
        for result in security_results
    )

    return RagEvaluationSummary(
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=failed_cases,
        retrieval_hit_rate=calculate_hit_rate(
            retrieval_results
        ),
        retrieval_recall_at_k=calculate_mean_recall_at_k(
            retrieval_results
        ),
        citation_correctness=citation_correctness,
        groundedness=groundedness,
        reliability_accuracy=reliability_accuracy,
        security_violations=security_violations,
        passed=False,
    )


def run_quality_gate(
    results: list[RagEvaluationResult],
    *,
    thresholds: RagQualityGateThresholds | None = None,
) -> tuple[RagEvaluationSummary, RagQualityGateResult]:
    summary = build_evaluation_summary(results)

    gate = evaluate_quality_gate(
        summary,
        thresholds=thresholds,
    )

    final_summary = summary.model_copy(
        update={
            "passed": gate.passed,
        }
    )

    return final_summary, gate