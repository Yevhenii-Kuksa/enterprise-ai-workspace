import uuid

from app.ai.citation_validation import validate_answer_citations
from app.retrieval.context import RagContext
from app.retrieval.evidence import CitationSource, EvidenceItem


def _citation_source(label: str) -> CitationSource:
    return CitationSource(
        label=label,
        evidence=EvidenceItem(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            document_version_id=uuid.uuid4(),
            document_title=f"Document {label}",
            content=f"Evidence for {label}",
            chunk_index=0,
            distance=0.1,
            page_number=None,
            section_title=None,
            source_locator=None,
            source_system=None,
            source_uri=None,
        ),
    )


def _rag_context() -> RagContext:
    sources = [
        _citation_source("S1"),
        _citation_source("S2"),
    ]

    return RagContext(
        query="Test query",
        sources=sources,
        context_text="",
    )


def test_validate_answer_citations_accepts_valid_labels() -> None:
    result = validate_answer_citations(
        answer_text="Answer based on [S1] and [S2].",
        context=_rag_context(),
    )

    assert result.used_labels == {"S1", "S2"}
    assert result.valid_labels == {"S1", "S2"}
    assert result.invalid_labels == set()
    assert result.citation_count == 2
    assert result.invalid_citation_count == 0


def test_validate_answer_citations_detects_invalid_label() -> None:
    result = validate_answer_citations(
        answer_text="Answer based on [S99].",
        context=_rag_context(),
    )

    assert result.used_labels == {"S99"}
    assert result.valid_labels == set()
    assert result.invalid_labels == {"S99"}
    assert result.citation_count == 1
    assert result.invalid_citation_count == 1


def test_validate_answer_citations_deduplicates_repeated_labels() -> None:
    result = validate_answer_citations(
        answer_text="Answer [S1]. More details [S1].",
        context=_rag_context(),
    )

    assert result.used_labels == {"S1"}
    assert result.valid_labels == {"S1"}
    assert result.invalid_labels == set()
    assert result.citation_count == 2
    assert result.invalid_citation_count == 0


def test_validate_answer_citations_handles_answer_without_citations() -> None:
    result = validate_answer_citations(
        answer_text="Answer without citations.",
        context=_rag_context(),
    )

    assert result.used_labels == set()
    assert result.valid_labels == set()
    assert result.invalid_labels == set()
    assert result.citation_count == 0
    assert result.invalid_citation_count == 0


def test_validate_answer_citations_separates_valid_and_invalid_labels() -> None:
    result = validate_answer_citations(
        answer_text="Answer based on [S1], [S2] and [S42].",
        context=_rag_context(),
    )

    assert result.used_labels == {"S1", "S2", "S42"}
    assert result.valid_labels == {"S1", "S2"}
    assert result.invalid_labels == {"S42"}
    assert result.citation_count == 3
    assert result.invalid_citation_count == 1