from openai import OpenAI


class OpenAIEmbeddingProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        dimensions: int,
        timeout_seconds: float = 30.0,
        max_retries: int = 2,
    ) -> None:
        if not api_key:
            raise ValueError("OpenAI API key must not be empty.")

        if not model_name:
            raise ValueError("Embedding model name must not be empty.")

        if dimensions <= 0:
            raise ValueError("Embedding dimensions must be greater than zero.")

        if timeout_seconds <= 0:
            raise ValueError("OpenAI timeout must be greater than zero.")

        if max_retries < 0 or max_retries > 5:
            raise ValueError("OpenAI max retries must be between 0 and 5.")

        self._model_name = model_name
        self._dimensions = dimensions
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._client = OpenAI(
            api_key=api_key,
            timeout=timeout_seconds,
            max_retries=max_retries,
        )

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimensions(self) -> int:
        return self._dimensions

    @property
    def timeout_seconds(self) -> float:
        return self._timeout_seconds

    @property
    def max_retries(self) -> int:
        return self._max_retries

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