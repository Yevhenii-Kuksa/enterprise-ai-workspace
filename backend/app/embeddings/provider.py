from dataclasses import dataclass
from typing import Protocol


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