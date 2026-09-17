from pydantic import BaseModel, Field

from app.ai.evaluation.schemas import RagEvaluationSummary


class RagQualityGateThresholds(BaseModel):
    minimum_hit_rate: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
    )
    minimum_recall_at_k: float = Field(
        default=0.90,
        ge=0.0,
        le=1.0,
    )
    minimum_citation_correctness: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )
    minimum_groundedness: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
    )
    minimum_reliability_accuracy: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
    )
    maximum_security_violations: int = Field(
        default=0,
        ge=0,
    )


class RagQualityGateResult(BaseModel):
    passed: bool
    reasons: list[str] = Field(default_factory=list)


def evaluate_quality_gate(
    summary: RagEvaluationSummary,
    *,
    thresholds: RagQualityGateThresholds | None = None,
) -> RagQualityGateResult:
    active_thresholds = (
        thresholds or RagQualityGateThresholds()
    )

    reasons: list[str] = []

    if (
        summary.retrieval_hit_rate
        < active_thresholds.minimum_hit_rate
    ):
        reasons.append("retrieval_hit_rate_below_threshold")

    if (
        summary.retrieval_recall_at_k
        < active_thresholds.minimum_recall_at_k
    ):
        reasons.append("retrieval_recall_at_k_below_threshold")

    if (
        summary.citation_correctness
        < active_thresholds.minimum_citation_correctness
    ):
        reasons.append("citation_correctness_below_threshold")

    if (
        summary.groundedness
        < active_thresholds.minimum_groundedness
    ):
        reasons.append("groundedness_below_threshold")

    if (
        summary.reliability_accuracy
        < active_thresholds.minimum_reliability_accuracy
    ):
        reasons.append("reliability_accuracy_below_threshold")

    if (
        summary.security_violations
        > active_thresholds.maximum_security_violations
    ):
        reasons.append("security_violations_above_threshold")

    return RagQualityGateResult(
        passed=not reasons,
        reasons=reasons,
    )