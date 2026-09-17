import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from time import perf_counter

from app.ai.citation_validation import (
    CitationValidationResult,
    validate_answer_citations,
)
from app.ai.provider import AIAnswerProvider
from app.ai.reliability.policy import (
    ReliabilityDecision,
    ReliabilityPolicyResult,
    evaluate_reliability_policy,
)
from app.ai.reliability.service import (
    ReliabilityResult,
    evaluate_reliability,
)
from app.core.trace_context import TraceContext
from app.retrieval.context import RagContext

logger = logging.getLogger("enterprise_ai_workspace.ai")

SYSTEM_PROMPT = (
    "You are an enterprise AI assistant. "
    "Answer only from the provided context. "
    "Do not invent facts. "
    "When using information from a source, cite it using its label, "
    "for example [S1] or [S2]. "
    "If the context is insufficient, say that the available sources "
    "do not provide enough information."
)


@dataclass(frozen=True, slots=True)
class GeneratedAnswer:
    text: str
    model_name: str
    citation_validation: CitationValidationResult
    reliability: ReliabilityResult | None = None
    reliability_policy: ReliabilityPolicyResult | None = None


def build_user_prompt(context: RagContext) -> str:
    return (
        f"Question:\n{context.query}\n\n"
        f"Context:\n{context.context_text}"
    )


def generate_grounded_answer(
    *,
    provider: AIAnswerProvider,
    context: RagContext,
    evaluated_at: datetime | None = None,
    max_evidence_distance: float | None = None,
    max_source_age: timedelta | None = None,
    conflict_count: int = 0,
    conflict_checked: bool = False,
    trace_context: TraceContext | None = None,
) -> GeneratedAnswer:
    if not context.sources:
        raise ValueError(
            "Cannot generate a grounded answer without evidence."
        )

    reliability: ReliabilityResult | None = None
    reliability_policy: ReliabilityPolicyResult | None = None

    reliability_requested = any(
        value is not None
        for value in (
            evaluated_at,
            max_evidence_distance,
            max_source_age,
        )
    )

    if reliability_requested:
        if (
            evaluated_at is None
            or max_evidence_distance is None
            or max_source_age is None
        ):
            raise ValueError(
                "Reliability evaluation requires evaluated_at, "
                "max_evidence_distance, and max_source_age."
            )

        reliability = evaluate_reliability(
            context=context,
            evaluated_at=evaluated_at,
            max_evidence_distance=max_evidence_distance,
            max_source_age=max_source_age,
            conflict_count=conflict_count,
            conflict_checked=conflict_checked,
        )

        reliability_policy = evaluate_reliability_policy(
            reliability
        )

        if reliability_policy.decision is ReliabilityDecision.REFUSE:
            raise ValueError(
                "Reliability policy refused answer generation: "
                + ", ".join(reliability_policy.reasons)
            )

    started_at = perf_counter()

    result = provider.generate_answer(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=build_user_prompt(context),
    )

    duration_ms = (perf_counter() - started_at) * 1000

    citation_validation = validate_answer_citations(
        answer_text=result.text,
        context=context,
    )

    if trace_context is not None:
        logger.info(
            "AI generation completed.",
            extra={
                "trace_id": str(trace_context.trace_id),
                "request_id": str(trace_context.request_id),
                "action_id": (
                    str(trace_context.action_id)
                    if trace_context.action_id is not None
                    else None
                ),
                "event_type": "ai_generation_completed",
                "model_name": result.model_name,
                "evidence_count": len(context.sources),
                "citation_count": (
                    citation_validation.citation_count
                ),
                "invalid_citation_count": (
                    citation_validation.invalid_citation_count
                ),
                "reliability_decision": (
                    reliability_policy.decision.value
                    if reliability_policy is not None
                    else None
                ),
                "duration_ms": duration_ms,
            },
        )

    if citation_validation.invalid_citation_count > 0:
        raise ValueError(
            "Generated answer contains invalid citations."
        )

    if citation_validation.citation_count == 0:
        raise ValueError(
            "Generated answer does not contain citations."
        )

    return GeneratedAnswer(
        text=result.text,
        model_name=result.model_name,
        citation_validation=citation_validation,
        reliability=reliability,
        reliability_policy=reliability_policy,
    )