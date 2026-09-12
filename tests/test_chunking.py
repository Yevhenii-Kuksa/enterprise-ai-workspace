from app.ingestion.chunking import (
    ChunkingConfig,
    calculate_chunk_sha256,
    chunk_text,
    normalize_text,
)


def test_normalize_text_converts_line_endings() -> None:
    text = "line 1\r\nline 2\rline 3"

    assert normalize_text(text) == "line 1\nline 2\nline 3"


def test_normalize_text_collapses_spaces_and_tabs() -> None:
    text = "alpha    beta\t\tgamma"

    assert normalize_text(text) == "alpha beta gamma"


def test_normalize_text_removes_spaces_around_newlines() -> None:
    text = "alpha   \n   beta"

    assert normalize_text(text) == "alpha\nbeta"


def test_normalize_text_collapses_excessive_blank_lines() -> None:
    text = "alpha\n\n\n\nbeta"

    assert normalize_text(text) == "alpha\n\nbeta"


def test_normalize_text_strips_outer_whitespace() -> None:
    text = "   alpha beta   \n\n"

    assert normalize_text(text) == "alpha beta"


def test_calculate_chunk_sha256_is_deterministic() -> None:
    content = "Nexalvora Industries"

    first_hash = calculate_chunk_sha256(content)
    second_hash = calculate_chunk_sha256(content)

    assert first_hash == second_hash


def test_calculate_chunk_sha256_uses_normalized_content() -> None:
    first_hash = calculate_chunk_sha256("Nexalvora    Industries")
    second_hash = calculate_chunk_sha256("Nexalvora Industries")

    assert first_hash == second_hash


def test_calculate_chunk_sha256_changes_when_content_changes() -> None:
    first_hash = calculate_chunk_sha256("Version 1")
    second_hash = calculate_chunk_sha256("Version 2")

    assert first_hash != second_hash


def test_calculate_chunk_sha256_returns_64_character_hex_digest() -> None:
    content_hash = calculate_chunk_sha256("test content")

    assert len(content_hash) == 64
    assert all(character in "0123456789abcdef" for character in content_hash)


def test_chunk_text_returns_empty_list_for_empty_content() -> None:
    assert chunk_text("") == []
    assert chunk_text("   \n\n   ") == []


def test_chunk_text_returns_single_chunk_for_short_content() -> None:
    chunks = chunk_text(
        "Alpha beta gamma",
        ChunkingConfig(
            max_characters=100,
            overlap_characters=10,
        ),
    )

    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].content == "Alpha beta gamma"
    assert chunks[0].content_sha256 == calculate_chunk_sha256(
        "Alpha beta gamma"
    )


def test_chunk_text_splits_content_with_overlap() -> None:
    chunks = chunk_text(
        "abcdefghij",
        ChunkingConfig(
            max_characters=6,
            overlap_characters=2,
        ),
    )

    assert [chunk.content for chunk in chunks] == [
        "abcdef",
        "efghij",
    ]
    assert [chunk.chunk_index for chunk in chunks] == [0, 1]


def test_chunk_text_is_deterministic() -> None:
    config = ChunkingConfig(
        max_characters=8,
        overlap_characters=2,
    )

    first_chunks = chunk_text("abcdefghijklmnop", config)
    second_chunks = chunk_text("abcdefghijklmnop", config)

    assert first_chunks == second_chunks


def test_chunk_text_normalizes_before_splitting() -> None:
    chunks = chunk_text(
        "Alpha    beta",
        ChunkingConfig(
            max_characters=100,
            overlap_characters=10,
        ),
    )

    assert len(chunks) == 1
    assert chunks[0].content == "Alpha beta"


def test_chunk_text_rejects_non_positive_max_characters() -> None:
    config = ChunkingConfig(
        max_characters=0,
        overlap_characters=0,
    )

    try:
        chunk_text("content", config)
    except ValueError as exc:
        assert str(exc) == "max_characters must be greater than zero."
    else:
        raise AssertionError("Expected ValueError.")


def test_chunk_text_rejects_negative_overlap() -> None:
    config = ChunkingConfig(
        max_characters=100,
        overlap_characters=-1,
    )

    try:
        chunk_text("content", config)
    except ValueError as exc:
        assert str(exc) == "overlap_characters must not be negative."
    else:
        raise AssertionError("Expected ValueError.")


def test_chunk_text_rejects_overlap_equal_to_max_characters() -> None:
    config = ChunkingConfig(
        max_characters=100,
        overlap_characters=100,
    )

    try:
        chunk_text("content", config)
    except ValueError as exc:
        assert str(exc) == (
            "overlap_characters must be smaller than max_characters."
        )
    else:
        raise AssertionError("Expected ValueError.")


def test_chunk_text_rejects_overlap_larger_than_max_characters() -> None:
    config = ChunkingConfig(
        max_characters=100,
        overlap_characters=101,
    )

    try:
        chunk_text("content", config)
    except ValueError as exc:
        assert str(exc) == (
            "overlap_characters must be smaller than max_characters."
        )
    else:
        raise AssertionError("Expected ValueError.")

    
def test_chunk_text_prefers_paragraph_boundary() -> None:
    text = "Alpha paragraph.\n\nBeta paragraph continues."

    chunks = chunk_text(
        text,
        ChunkingConfig(
            max_characters=25,
            overlap_characters=0,
        ),
    )

    assert chunks[0].content == "Alpha paragraph."


def test_chunk_text_prefers_line_boundary() -> None:
    text = "Alpha line\nBeta line continues."

    chunks = chunk_text(
        text,
        ChunkingConfig(
            max_characters=18,
            overlap_characters=0,
        ),
    )

    assert chunks[0].content == "Alpha line"


def test_chunk_text_prefers_sentence_boundary() -> None:
    text = "Alpha sentence. Beta sentence continues."

    chunks = chunk_text(
        text,
        ChunkingConfig(
            max_characters=25,
            overlap_characters=0,
        ),
    )

    assert chunks[0].content == "Alpha sentence."