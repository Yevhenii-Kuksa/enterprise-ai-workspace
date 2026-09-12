import hashlib
import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChunkingConfig:
    max_characters: int = 2000
    overlap_characters: int = 200


@dataclass(frozen=True, slots=True)
class TextChunk:
    chunk_index: int
    content: str
    content_sha256: str
    token_count: int | None = None
    page_number: int | None = None
    section_title: str | None = None
    source_locator: dict[str, object] | None = None


def normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r" *\n *", "\n", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)

    return normalized.strip()


def calculate_chunk_sha256(content: str) -> str:
    normalized_content = normalize_text(content)
    return hashlib.sha256(normalized_content.encode("utf-8")).hexdigest()


def _find_natural_boundary(
    text: str,
    start: int,
    hard_end: int,
) -> int:
    if hard_end >= len(text):
        return len(text)

    search_window = text[start:hard_end]

    paragraph_boundary = search_window.rfind("\n\n")
    if paragraph_boundary > 0:
        return start + paragraph_boundary

    line_boundary = search_window.rfind("\n")
    if line_boundary > 0:
        return start + line_boundary

    sentence_boundary = max(
        search_window.rfind(". "),
        search_window.rfind("! "),
        search_window.rfind("? "),
    )
    if sentence_boundary > 0:
        return start + sentence_boundary + 1

    return hard_end


def chunk_text(
    text: str,
    config: ChunkingConfig | None = None,
) -> list[TextChunk]:
    chunking_config = config or ChunkingConfig()

    if chunking_config.max_characters <= 0:
        raise ValueError("max_characters must be greater than zero.")

    if chunking_config.overlap_characters < 0:
        raise ValueError("overlap_characters must not be negative.")

    if chunking_config.overlap_characters >= chunking_config.max_characters:
        raise ValueError(
            "overlap_characters must be smaller than max_characters."
        )

    normalized_text = normalize_text(text)

    if not normalized_text:
        return []

    chunks: list[TextChunk] = []
    start = 0
    chunk_index = 0

    while start < len(normalized_text):
        hard_end = min(
            start + chunking_config.max_characters,
            len(normalized_text),
        )

        end = _find_natural_boundary(
            normalized_text,
            start,
            hard_end,
        )

        chunk_content = normalized_text[start:end].strip()

        if chunk_content:
            chunks.append(
                TextChunk(
                    chunk_index=chunk_index,
                    content=chunk_content,
                    content_sha256=calculate_chunk_sha256(chunk_content),
                )
            )
            chunk_index += 1

        if end == len(normalized_text):
            break

        next_start = end - chunking_config.overlap_characters

        if next_start <= start:
            next_start = end

        start = next_start

    return chunks