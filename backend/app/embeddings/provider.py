from dataclasses import dataclass
from typing import Protocol


class EmbeddingProviderError(RuntimeError):
    """Raised when an external embedding provider cannot complete a request."""


@dataclass(frozen=True, slots=True)
class EmbeddingResult:
    model_name: str
    dimensions: int
    vector: list[float]


class EmbeddingProvider(Protocol):
    @property
    def model_name(self) -> str:
        ...

    @property
    def dimensions(self) -> int:
        ...

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        ...