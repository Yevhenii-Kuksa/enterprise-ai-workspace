import re
from dataclasses import dataclass

from app.retrieval.context import RagContext

_CITATION_PATTERN = re.compile(r"\[(S\d+)\]")


@dataclass(frozen=True, slots=True)
class CitationValidationResult:
    used_labels: set[str]
    valid_labels: set[str]
    invalid_labels: set[str]
    citation_count: int
    invalid_citation_count: int


def validate_answer_citations(
    *,
    answer_text: str,
    context: RagContext,
) -> CitationValidationResult:
    citation_matches = _CITATION_PATTERN.findall(answer_text)

    used_labels = set(citation_matches)
    allowed_labels = {
        source.label
        for source in context.sources
    }

    valid_labels = used_labels & allowed_labels
    invalid_labels = used_labels - allowed_labels

    return CitationValidationResult(
        used_labels=used_labels,
        valid_labels=valid_labels,
        invalid_labels=invalid_labels,
        citation_count=len(citation_matches),
        invalid_citation_count=sum(
            label not in allowed_labels
            for label in citation_matches
        ),
    )