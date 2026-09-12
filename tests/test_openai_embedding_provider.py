from dataclasses import dataclass

from app.embeddings.openai_provider import OpenAIEmbeddingProvider


@dataclass
class FakeEmbeddingItem:
    index: int
    embedding: list[float]


@dataclass
class FakeEmbeddingResponse:
    data: list[FakeEmbeddingItem]


class FakeEmbeddingsClient:
    def __init__(
        self,
        response: FakeEmbeddingResponse,
    ) -> None:
        self._response = response
        self.calls: list[dict[str, object]] = []

    def create(
        self,
        *,
        model: str,
        input: list[str],
        dimensions: int,
    ) -> FakeEmbeddingResponse:
        self.calls.append(
            {
                "model": model,
                "input": input,
                "dimensions": dimensions,
            }
        )
        return self._response


class FakeOpenAIClient:
    def __init__(
        self,
        response: FakeEmbeddingResponse,
    ) -> None:
        self.embeddings = FakeEmbeddingsClient(response)


def test_openai_embedding_provider_rejects_empty_api_key() -> None:
    try:
        OpenAIEmbeddingProvider(
            api_key="",
            model_name="test-model",
            dimensions=3,
        )
    except ValueError as exc:
        assert str(exc) == "OpenAI API key must not be empty."
    else:
        raise AssertionError("Expected ValueError.")


def test_openai_embedding_provider_rejects_empty_model_name() -> None:
    try:
        OpenAIEmbeddingProvider(
            api_key="test-key",
            model_name="",
            dimensions=3,
        )
    except ValueError as exc:
        assert str(exc) == "Embedding model name must not be empty."
    else:
        raise AssertionError("Expected ValueError.")


def test_openai_embedding_provider_rejects_invalid_dimensions() -> None:
    try:
        OpenAIEmbeddingProvider(
            api_key="test-key",
            model_name="test-model",
            dimensions=0,
        )
    except ValueError as exc:
        assert str(exc) == "Embedding dimensions must be greater than zero."
    else:
        raise AssertionError("Expected ValueError.")


def test_openai_embedding_provider_returns_empty_list_for_empty_input() -> None:
    provider = OpenAIEmbeddingProvider(
        api_key="test-key",
        model_name="test-model",
        dimensions=3,
    )

    assert provider.embed_texts([]) == []


def test_openai_embedding_provider_sorts_vectors_by_index() -> None:
    provider = OpenAIEmbeddingProvider(
        api_key="test-key",
        model_name="test-model",
        dimensions=3,
    )

    fake_client = FakeOpenAIClient(
        FakeEmbeddingResponse(
            data=[
                FakeEmbeddingItem(
                    index=1,
                    embedding=[0.0, 1.0, 0.0],
                ),
                FakeEmbeddingItem(
                    index=0,
                    embedding=[1.0, 0.0, 0.0],
                ),
            ]
        )
    )

    provider._client = fake_client  # type: ignore[assignment]

    result = provider.embed_texts(
        [
            "first text",
            "second text",
        ]
    )

    assert result == [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]

    assert fake_client.embeddings.calls == [
        {
            "model": "test-model",
            "input": [
                "first text",
                "second text",
            ],
            "dimensions": 3,
        }
    ]