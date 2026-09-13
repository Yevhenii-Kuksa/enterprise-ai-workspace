import uuid

from app.retrieval.evidence import (
    build_citation_sources,
    build_evidence_items,
)
from app.retrieval.vector_search import VectorSearchResult


def test_build_evidence_items_returns_empty_list_for_empty_input() -> None:
    assert build_evidence_items([]) == []


def test_build_evidence_items_preserves_all_fields() -> None:
    chunk_id = uuid.uuid4()
    document_id = uuid.uuid4()
    document_version_id = uuid.uuid4()

    results = [
        VectorSearchResult(
            chunk_id=chunk_id,
            document_id=document_id,
            document_version_id=document_version_id,
            document_title="Procedura magazynowa",
            content="Treść fragmentu dokumentu.",
            chunk_index=2,
            distance=0.123,
            page_number=7,
            section_title="Przyjęcie towaru",
            source_locator={
                "page": 7,
                "paragraph": 3,
            },
            source_system="sharepoint",
            source_uri="https://example.test/procedura-magazynowa",
        )
    ]

    evidence = build_evidence_items(results)

    assert len(evidence) == 1

    item = evidence[0]

    assert item.chunk_id == chunk_id
    assert item.document_id == document_id
    assert item.document_version_id == document_version_id
    assert item.document_title == "Procedura magazynowa"
    assert item.content == "Treść fragmentu dokumentu."
    assert item.chunk_index == 2
    assert item.distance == 0.123
    assert item.page_number == 7
    assert item.section_title == "Przyjęcie towaru"
    assert item.source_locator == {
        "page": 7,
        "paragraph": 3,
    }
    assert item.source_system == "sharepoint"
    assert (
        item.source_uri
        == "https://example.test/procedura-magazynowa"
    )


def test_build_evidence_items_preserves_result_order() -> None:
    first_chunk_id = uuid.uuid4()
    second_chunk_id = uuid.uuid4()

    results = [
        VectorSearchResult(
            chunk_id=first_chunk_id,
            document_id=uuid.uuid4(),
            document_version_id=uuid.uuid4(),
            document_title="First document",
            content="First evidence",
            chunk_index=0,
            distance=0.1,
            page_number=None,
            section_title=None,
            source_locator=None,
            source_system=None,
            source_uri=None,
        ),
        VectorSearchResult(
            chunk_id=second_chunk_id,
            document_id=uuid.uuid4(),
            document_version_id=uuid.uuid4(),
            document_title="Second document",
            content="Second evidence",
            chunk_index=1,
            distance=0.2,
            page_number=None,
            section_title=None,
            source_locator=None,
            source_system=None,
            source_uri=None,
        ),
    ]

    evidence = build_evidence_items(results)

    assert [item.chunk_id for item in evidence] == [
        first_chunk_id,
        second_chunk_id,
    ]
    assert [item.distance for item in evidence] == [
        0.1,
        0.2,
    ]

def test_build_citation_sources_assigns_stable_labels() -> None:
    evidence = build_evidence_items(
        [
            VectorSearchResult(
                chunk_id=uuid.uuid4(),
                document_id=uuid.uuid4(),
                document_version_id=uuid.uuid4(),
                document_title="First document",
                content="First evidence",
                chunk_index=0,
                distance=0.1,
                page_number=None,
                section_title=None,
                source_locator=None,
                source_system=None,
                source_uri=None,
            ),
            VectorSearchResult(
                chunk_id=uuid.uuid4(),
                document_id=uuid.uuid4(),
                document_version_id=uuid.uuid4(),
                document_title="Second document",
                content="Second evidence",
                chunk_index=1,
                distance=0.2,
                page_number=None,
                section_title=None,
                source_locator=None,
                source_system=None,
                source_uri=None,
            ),
        ]
    )

    citations = build_citation_sources(evidence)

    assert [citation.label for citation in citations] == [
        "S1",
        "S2",
    ]

    assert citations[0].evidence == evidence[0]
    assert citations[1].evidence == evidence[1]


def test_build_citation_sources_returns_empty_list_for_empty_evidence() -> None:
    assert build_citation_sources([]) == []