from dataclasses import dataclass

from app.ai.citation_validation import (
    CitationValidationResult,
    validate_answer_citations,
)
from app.ai.provider import AIAnswerProvider
from app.retrieval.context import RagContext

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


def build_user_prompt(context: RagContext) -> str:
    return (
        f"Question:\n{context.query}\n\n"
        f"Context:\n{context.context_text}"
    )


def generate_grounded_answer(
    *,
    provider: AIAnswerProvider,
    context: RagContext,
) -> GeneratedAnswer:
    if not context.sources:
        raise ValueError(
            "Cannot generate a grounded answer without evidence."
        )

    result = provider.generate_answer(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=build_user_prompt(context),
    )

    citation_validation = validate_answer_citations(
        answer_text=result.text,
        context=context,
    )

    return GeneratedAnswer(
        text=result.text,
        model_name=result.model_name,
        citation_validation=citation_validation,
    )