import logging
from dataclasses import dataclass
from time import perf_counter

from sqlalchemy.orm import Session

from app.core.error_taxonomy import ErrorCategory
from app.core.trace_context import TraceContext
from app.embeddings.provider import EmbeddingProvider
from app.embeddings.service import generate_embeddings
from app.retrieval.context import RagContext, build_rag_context
from app.retrieval.evidence import (
    build_citation_sources,
    build_evidence_items,
)
from app.retrieval.vector_search import (
    VectorSearchResult,
    search_similar_chunks,
)
from app.security.current_user import CurrentUser

logger = logging.getLogger("enterprise_ai_workspace.retrieval")


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    query: str
    evidence: list[VectorSearchResult]


def _log_retrieval_failure(
    *,
    trace_context: TraceContext | None,
    current_user: CurrentUser,
    limit: int,
    started_at: float,
    exc: Exception,
    error_category: ErrorCategory,
) -> None:
    if trace_context is None:
        return

    duration_ms = (perf_counter() - started_at) * 1000

    logger.error(
        "Retrieval failed.",
        extra={
            "trace_id": str(trace_context.trace_id),
            "request_id": str(trace_context.request_id),
            "action_id": (
                str(trace_context.action_id)
                if trace_context.action_id is not None
                else None
            ),
            "event_type": "retrieval_failed",
            "organization_id": str(
                current_user.organization_id
            ),
            "user_id": str(current_user.id),
            "requested_limit": limit,
            "error_type": type(exc).__name__,
            "error_category": error_category.value,
            "duration_ms": duration_ms,
        },
    )


def retrieve_evidence(
    session: Session,
    *,
    current_user: CurrentUser,
    query: str,
    embedding_provider: EmbeddingProvider,
    limit: int = 10,
    trace_context: TraceContext | None = None,
) -> RetrievalResult:
    normalized_query = query.strip()

    if not normalized_query:
        raise ValueError("Query must not be empty.")

    started_at = perf_counter()

    try:
        query_embeddings = generate_embeddings(
            embedding_provider,
            [normalized_query],
        )
    except Exception as exc:
        _log_retrieval_failure(
            trace_context=trace_context,
            current_user=current_user,
            limit=limit,
            started_at=started_at,
            exc=exc,
            error_category=ErrorCategory.DEPENDENCY,
        )
        raise

    if len(query_embeddings) != 1:
        embedding_error = RuntimeError(
            "Expected exactly one query embedding."
        )

        _log_retrieval_failure(
            trace_context=trace_context,
            current_user=current_user,
            limit=limit,
            started_at=started_at,
            exc=embedding_error,
            error_category=ErrorCategory.DEPENDENCY,
        )

        raise embedding_error

    query_embedding = query_embeddings[0]

    try:
        evidence = search_similar_chunks(
            session,
            current_user=current_user,
            query_embedding=query_embedding.vector,
            embedding_model=query_embedding.model_name,
            limit=limit,
        )
    except Exception as exc:
        _log_retrieval_failure(
            trace_context=trace_context,
            current_user=current_user,
            limit=limit,
            started_at=started_at,
            exc=exc,
            error_category=ErrorCategory.DATABASE,
        )
        raise

    duration_ms = (perf_counter() - started_at) * 1000

    if trace_context is not None:
        best_distance = (
            min(item.distance for item in evidence)
            if evidence
            else None
        )

        logger.info(
            "Retrieval completed.",
            extra={
                "trace_id": str(trace_context.trace_id),
                "request_id": str(trace_context.request_id),
                "action_id": (
                    str(trace_context.action_id)
                    if trace_context.action_id is not None
                    else None
                ),
                "event_type": "retrieval_completed",
                "organization_id": str(
                    current_user.organization_id
                ),
                "user_id": str(current_user.id),
                "embedding_model": query_embedding.model_name,
                "requested_limit": limit,
                "evidence_count": len(evidence),
                "best_distance": best_distance,
                "duration_ms": duration_ms,
            },
        )

    return RetrievalResult(
        query=normalized_query,
        evidence=evidence,
    )


def prepare_rag_context(
    session: Session,
    *,
    current_user: CurrentUser,
    query: str,
    embedding_provider: EmbeddingProvider,
    limit: int = 10,
    trace_context: TraceContext | None = None,
) -> RagContext:
    retrieval_result = retrieve_evidence(
        session,
        current_user=current_user,
        query=query,
        embedding_provider=embedding_provider,
        limit=limit,
        trace_context=trace_context,
    )

    evidence_items = build_evidence_items(
        retrieval_result.evidence,
    )

    citation_sources = build_citation_sources(
        evidence_items,
    )

    return build_rag_context(
        query=retrieval_result.query,
        sources=citation_sources,
    )