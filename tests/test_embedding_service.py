from app.embeddings.service import generate_embeddings


class FakeEmbeddingProvider:
    def __init__(
        self,
        *,
        model_name: str = "test-model",
        dimensions: int = 3,
        vectors: list[list[float]] | None = None,
    ) -> None:
        self._model_name = model_name
        self._dimensions = dimensions
        self._vectors = vectors or []

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return self._vectors


def test_generate_embeddings_returns_empty_list_for_empty_input() -> None:
    provider = FakeEmbeddingProvider()

    assert generate_embeddings(provider, []) == []


def test_generate_embeddings_returns_results_for_valid_vectors() -> None:
    provider = FakeEmbeddingProvider(
        model_name="test-model",
        dimensions=3,
        vectors=[
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
    )

    results = generate_embeddings(
        provider,
        ["first text", "second text"],
    )

    assert len(results) == 2

    assert results[0].model_name == "test-model"
    assert results[0].dimensions == 3
    assert results[0].vector == [1.0, 0.0, 0.0]

    assert results[1].model_name == "test-model"
    assert results[1].dimensions == 3
    assert results[1].vector == [0.0, 1.0, 0.0]


def test_generate_embeddings_rejects_wrong_vector_count() -> None:
    provider = FakeEmbeddingProvider(
        dimensions=3,
        vectors=[
            [1.0, 0.0, 0.0],
        ],
    )

    try:
        generate_embeddings(
            provider,
            ["first text", "second text"],
        )
    except ValueError as exc:
        assert str(exc) == (
            "Embedding provider returned a different number of vectors than texts."
        )
    else:
        raise AssertionError("Expected ValueError.")


def test_generate_embeddings_rejects_wrong_dimensions() -> None:
    provider = FakeEmbeddingProvider(
        dimensions=3,
        vectors=[
            [1.0, 0.0],
        ],
    )

    try:
        generate_embeddings(
            provider,
            ["first text"],
        )
    except ValueError as exc:
        assert str(exc) == (
            "Embedding vector dimensions do not match provider dimensions."
        )
    else:
        raise AssertionError("Expected ValueError.")