from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.ai.answer_service import GeneratedAnswer, generate_grounded_answer
from app.ai.factory import create_ai_answer_provider
from app.ai.provider import AIAnswerProvider
from app.core.config import Settings
from app.core.trace_context import TraceContext
from app.embeddings.factory import create_embedding_provider
from app.embeddings.provider import EmbeddingProvider
from app.retrieval.context import RagContext
from app.retrieval.service import prepare_rag_context
from app.security.current_user import CurrentUser


@dataclass(frozen=True, slots=True)
class RagAnswerResult:
    context: RagContext
    answer: GeneratedAnswer


def answer_rag_query(
    session: Session,
    *,
    current_user: CurrentUser,
    query: str,
    embedding_provider: EmbeddingProvider,
    ai_answer_provider: AIAnswerProvider,
    evaluated_at: datetime,
    max_evidence_distance: float,
    max_source_age: timedelta,
    retrieval_limit: int = 10,
    conflict_count: int = 0,
    conflict_checked: bool = False,
    trace_context: TraceContext | None = None,
) -> RagAnswerResult:
    context = prepare_rag_context(
        session,
        current_user=current_user,
        query=query,
        embedding_provider=embedding_provider,
        limit=retrieval_limit,
        trace_context=trace_context,
    )

    answer = generate_grounded_answer(
        provider=ai_answer_provider,
        context=context,
        evaluated_at=evaluated_at,
        max_evidence_distance=max_evidence_distance,
        max_source_age=max_source_age,
        conflict_count=conflict_count,
        conflict_checked=conflict_checked,
    )

    return RagAnswerResult(
        context=context,
        answer=answer,
    )


def answer_rag_query_from_settings(
    session: Session,
    *,
    current_user: CurrentUser,
    query: str,
    settings: Settings,
    retrieval_limit: int = 10,
    conflict_count: int = 0,
    conflict_checked: bool = False,
    evaluated_at: datetime | None = None,
    trace_context: TraceContext | None = None,
) -> RagAnswerResult:
    embedding_provider = create_embedding_provider(settings)
    ai_answer_provider = create_ai_answer_provider(settings)

    effective_evaluated_at = (
        evaluated_at
        if evaluated_at is not None
        else datetime.now(UTC)
    )

    return answer_rag_query(
        session,
        current_user=current_user,
        query=query,
        embedding_provider=embedding_provider,
        ai_answer_provider=ai_answer_provider,
        evaluated_at=effective_evaluated_at,
        max_evidence_distance=(
            settings.ai_reliability_max_evidence_distance
        ),
        max_source_age=timedelta(
            days=settings.ai_reliability_max_source_age_days
        ),
        retrieval_limit=retrieval_limit,
        conflict_count=conflict_count,
        conflict_checked=conflict_checked,
        trace_context=trace_context,
    )