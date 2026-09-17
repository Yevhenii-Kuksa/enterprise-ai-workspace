from app.ai.evaluation.quality_gate import (
    RagQualityGateThresholds,
    evaluate_quality_gate,
)
from app.ai.evaluation.schemas import RagEvaluationSummary


def _summary(
    *,
    retrieval_hit_rate: float = 1.0,
    retrieval_recall_at_k: float = 1.0,
    citation_correctness: float = 1.0,
    groundedness: float = 1.0,
    reliability_accuracy: float = 1.0,
    security_violations: int = 0,
) -> RagEvaluationSummary:
    return RagEvaluationSummary(
        total_cases=10,
        passed_cases=10,
        failed_cases=0,
        retrieval_hit_rate=retrieval_hit_rate,
        retrieval_recall_at_k=retrieval_recall_at_k,
        citation_correctness=citation_correctness,
        groundedness=groundedness,
        reliability_accuracy=reliability_accuracy,
        security_violations=security_violations,
        passed=True,
    )


def test_quality_gate_passes_when_all_metrics_meet_thresholds() -> None:
    result = evaluate_quality_gate(
        _summary(),
    )

    assert result.passed is True
    assert result.reasons == []


def test_quality_gate_accepts_metrics_exactly_at_thresholds() -> None:
    result = evaluate_quality_gate(
        _summary(
            retrieval_hit_rate=0.95,
            retrieval_recall_at_k=0.90,
            citation_correctness=1.0,
            groundedness=0.95,
            reliability_accuracy=0.95,
            security_violations=0,
        )
    )

    assert result.passed is True
    assert result.reasons == []


def test_quality_gate_fails_low_hit_rate() -> None:
    result = evaluate_quality_gate(
        _summary(
            retrieval_hit_rate=0.94,
        )
    )

    assert result.passed is False
    assert result.reasons == [
        "retrieval_hit_rate_below_threshold",
    ]


def test_quality_gate_fails_low_recall_at_k() -> None:
    result = evaluate_quality_gate(
        _summary(
            retrieval_recall_at_k=0.89,
        )
    )

    assert result.passed is False
    assert result.reasons == [
        "retrieval_recall_at_k_below_threshold",
    ]


def test_quality_gate_fails_low_citation_correctness() -> None:
    result = evaluate_quality_gate(
        _summary(
            citation_correctness=0.99,
        )
    )

    assert result.passed is False
    assert result.reasons == [
        "citation_correctness_below_threshold",
    ]


def test_quality_gate_fails_low_groundedness() -> None:
    result = evaluate_quality_gate(
        _summary(
            groundedness=0.94,
        )
    )

    assert result.passed is False
    assert result.reasons == [
        "groundedness_below_threshold",
    ]


def test_quality_gate_fails_low_reliability_accuracy() -> None:
    result = evaluate_quality_gate(
        _summary(
            reliability_accuracy=0.94,
        )
    )

    assert result.passed is False
    assert result.reasons == [
        "reliability_accuracy_below_threshold",
    ]


def test_quality_gate_fails_security_regression() -> None:
    result = evaluate_quality_gate(
        _summary(
            security_violations=1,
        )
    )

    assert result.passed is False
    assert result.reasons == [
        "security_violations_above_threshold",
    ]


def test_quality_gate_reports_all_failed_metrics() -> None:
    result = evaluate_quality_gate(
        _summary(
            retrieval_hit_rate=0.80,
            retrieval_recall_at_k=0.70,
            citation_correctness=0.90,
            groundedness=0.80,
            reliability_accuracy=0.75,
            security_violations=2,
        )
    )

    assert result.passed is False
    assert result.reasons == [
        "retrieval_hit_rate_below_threshold",
        "retrieval_recall_at_k_below_threshold",
        "citation_correctness_below_threshold",
        "groundedness_below_threshold",
        "reliability_accuracy_below_threshold",
        "security_violations_above_threshold",
    ]


def test_quality_gate_supports_custom_thresholds() -> None:
    thresholds = RagQualityGateThresholds(
        minimum_hit_rate=0.80,
        minimum_recall_at_k=0.75,
        minimum_citation_correctness=0.90,
        minimum_groundedness=0.85,
        minimum_reliability_accuracy=0.85,
        maximum_security_violations=0,
    )

    result = evaluate_quality_gate(
        _summary(
            retrieval_hit_rate=0.85,
            retrieval_recall_at_k=0.80,
            citation_correctness=0.95,
            groundedness=0.90,
            reliability_accuracy=0.90,
        ),
        thresholds=thresholds,
    )

    assert result.passed is True
    assert result.reasons == []