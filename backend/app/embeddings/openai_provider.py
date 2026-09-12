from openai import OpenAI


class OpenAIEmbeddingProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        dimensions: int,
    ) -> None:
        if not api_key:
            raise ValueError("OpenAI API key must not be empty.")

        if not model_name:
            raise ValueError("Embedding model name must not be empty.")

        if dimensions <= 0:
            raise ValueError("Embedding dimensions must be greater than zero.")

        self._model_name = model_name
        self._dimensions = dimensions
        self._client = OpenAI(api_key=api_key)

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
        if not texts:
            return []

        response = self._client.embeddings.create(
            model=self._model_name,
            input=texts,
            dimensions=self._dimensions,
        )

        embeddings = sorted(
            response.data,
            key=lambda item: item.index,
        )

        return [item.embedding for item in embeddings]