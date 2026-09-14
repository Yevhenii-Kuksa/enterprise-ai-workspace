from dataclasses import dataclass

from app.retrieval.evidence import CitationSource


@dataclass(frozen=True, slots=True)
class RagContext:
    query: str
    sources: list[CitationSource]
    context_text: str


def _build_source_block(source: CitationSource) -> str:
    lines = [
        f"[{source.label}]",
        f"Document: {source.evidence.document_title}",
    ]

    if source.evidence.page_number is not None:
        lines.append(f"Page: {source.evidence.page_number}")

    if source.evidence.section_title is not None:
        lines.append(f"Section: {source.evidence.section_title}")

    if source.evidence.source_system is not None:
        lines.append(f"Source system: {source.evidence.source_system}")

    if source.evidence.source_uri is not None:
        lines.append(f"Source URI: {source.evidence.source_uri}")

    lines.append(f"Content: {source.evidence.content}")

    return "\n".join(lines)


def build_rag_context(
    *,
    query: str,
    sources: list[CitationSource],
) -> RagContext:
    normalized_query = query.strip()

    if not normalized_query:
        raise ValueError("Query must not be empty.")

    context_blocks = [
        _build_source_block(source)
        for source in sources
    ]

    context_text = "\n\n".join(context_blocks)

    return RagContext(
        query=normalized_query,
        sources=sources,
        context_text=context_text,
    )