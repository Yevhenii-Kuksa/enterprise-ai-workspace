import uuid

from app.retrieval.context import build_rag_context
from app.retrieval.evidence import CitationSource, EvidenceItem


def _evidence_item(
    *,
    title: str,
    content: str,
    distance: float,
    page_number: int | None = None,
    section_title: str | None = None,
    source_system: str | None = None,
    source_uri: str | None = None,
) -> EvidenceItem:
    return EvidenceItem(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        document_version_id=uuid.uuid4(),
        document_title=title,
        content=content,
        chunk_index=0,
        distance=distance,
        page_number=page_number,
        section_title=section_title,
        source_locator=None,
        source_system=source_system,
        source_uri=source_uri,
        source_modified_at=None,
    )


def test_build_rag_context_rejects_empty_query() -> None:
    try:
        build_rag_context(
            query="   ",
            sources=[],
        )
    except ValueError as exc:
        assert str(exc) == "Query must not be empty."
    else:
        raise AssertionError("Expected ValueError.")


def test_build_rag_context_normalizes_query() -> None:
    context = build_rag_context(
        query="  Jak wygląda procedura?  ",
        sources=[],
    )

    assert context.query == "Jak wygląda procedura?"
    assert context.sources == []
    assert context.context_text == ""


def test_build_rag_context_preserves_source_order_and_labels() -> None:
    sources = [
        CitationSource(
            label="S1",
            evidence=_evidence_item(
                title="Procedura magazynowa",
                content="Pierwszy fragment.",
                distance=0.1,
            ),
        ),
        CitationSource(
            label="S2",
            evidence=_evidence_item(
                title="Instrukcja jakości",
                content="Drugi fragment.",
                distance=0.2,
            ),
        ),
    ]

    context = build_rag_context(
        query="Jak wygląda procedura?",
        sources=sources,
    )

    assert context.sources == sources
    assert "[S1]" in context.context_text
    assert "[S2]" in context.context_text
    assert context.context_text.index("[S1]") < context.context_text.index("[S2]")


def test_build_rag_context_includes_document_title_and_content() -> None:
    source = CitationSource(
        label="S1",
        evidence=_evidence_item(
            title="Procedura magazynowa",
            content="Towar należy przyjąć zgodnie z instrukcją.",
            distance=0.1,
        ),
    )

    context = build_rag_context(
        query="Jak przyjąć towar?",
        sources=[source],
    )

    assert "Document: Procedura magazynowa" in context.context_text
    assert (
        "Content: Towar należy przyjąć zgodnie z instrukcją."
        in context.context_text
    )


def test_build_rag_context_includes_citation_metadata() -> None:
    source = CitationSource(
        label="S1",
        evidence=_evidence_item(
            title="Procedura magazynowa",
            content="Towar należy przyjąć zgodnie z instrukcją.",
            distance=0.1,
            page_number=4,
            section_title="Przyjęcie towaru",
            source_system="sharepoint",
            source_uri="https://example.test/procedura-magazynowa",
        ),
    )

    context = build_rag_context(
        query="Jak przyjąć towar?",
        sources=[source],
    )

    assert "Page: 4" in context.context_text
    assert "Section: Przyjęcie towaru" in context.context_text
    assert "Source system: sharepoint" in context.context_text
    assert (
        "Source URI: https://example.test/procedura-magazynowa"
        in context.context_text
    )


def test_build_rag_context_omits_missing_optional_metadata() -> None:
    source = CitationSource(
        label="S1",
        evidence=_evidence_item(
            title="Procedura magazynowa",
            content="Treść dokumentu.",
            distance=0.1,
        ),
    )

    context = build_rag_context(
        query="Pytanie",
        sources=[source],
    )

    assert "Page:" not in context.context_text
    assert "Section:" not in context.context_text
    assert "Source system:" not in context.context_text
    assert "Source URI:" not in context.context_text


def test_build_rag_context_returns_empty_context_for_no_sources() -> None:
    context = build_rag_context(
        query="Pytanie bez źródeł",
        sources=[],
    )

    assert context.sources == []
    assert context.context_text == ""