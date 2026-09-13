import uuid
from dataclasses import dataclass

from app.retrieval.vector_search import VectorSearchResult


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_version_id: uuid.UUID
    document_title: str
    content: str
    chunk_index: int
    distance: float
    page_number: int | None
    section_title: str | None
    source_locator: dict[str, object] | None
    source_system: str | None
    source_uri: str | None

@dataclass(frozen=True, slots=True)
class CitationSource:
    label: str
    evidence: EvidenceItem


def build_evidence_items(
    results: list[VectorSearchResult],
) -> list[EvidenceItem]:
    return [
        EvidenceItem(
            chunk_id=result.chunk_id,
            document_id=result.document_id,
            document_version_id=result.document_version_id,
            document_title=result.document_title,
            content=result.content,
            chunk_index=result.chunk_index,
            distance=result.distance,
            page_number=result.page_number,
            section_title=result.section_title,
            source_locator=result.source_locator,
            source_system=result.source_system,
            source_uri=result.source_uri,
        )
        for result in results
    ]

def build_citation_sources(
    evidence: list[EvidenceItem],
) -> list[CitationSource]:
    return [
        CitationSource(
            label=f"S{index}",
            evidence=item,
        )
        for index, item in enumerate(evidence, start=1)
    ]