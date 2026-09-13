from dataclasses import dataclass

from sqlalchemy.orm import Session

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


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    query: str
    evidence: list[VectorSearchResult]


def retrieve_evidence(
    session: Session,
    *,
    current_user: CurrentUser,
    query: str,
    embedding_provider: EmbeddingProvider,
    limit: int = 10,
) -> RetrievalResult:
    normalized_query = query.strip()

    if not normalized_query:
        raise ValueError("Query must not be empty.")

    query_embeddings = generate_embeddings(
        embedding_provider,
        [normalized_query],
    )

    if len(query_embeddings) != 1:
        raise RuntimeError("Expected exactly one query embedding.")

    query_embedding = query_embeddings[0]

    evidence = search_similar_chunks(
        session,
        current_user=current_user,
        query_embedding=query_embedding.vector,
        embedding_model=query_embedding.model_name,
        limit=limit,
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
) -> RagContext:
    retrieval_result = retrieve_evidence(
        session,
        current_user=current_user,
        query=query,
        embedding_provider=embedding_provider,
        limit=limit,
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