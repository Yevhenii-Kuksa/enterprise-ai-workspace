from dataclasses import dataclass

from app.retrieval.evidence import CitationSource


@dataclass(frozen=True, slots=True)
class RagContext:
    query: str
    sources: list[CitationSource]
    context_text: str


def build_rag_context(
    *,
    query: str,
    sources: list[CitationSource],
) -> RagContext:
    normalized_query = query.strip()

    if not normalized_query:
        raise ValueError("Query must not be empty.")

    context_blocks = [
        (
            f"[{source.label}]\n"
            f"Document: {source.evidence.document_title}\n"
            f"Content: {source.evidence.content}"
        )
        for source in sources
    ]

    context_text = "\n\n".join(context_blocks)

    return RagContext(
        query=normalized_query,
        sources=sources,
        context_text=context_text,
    )