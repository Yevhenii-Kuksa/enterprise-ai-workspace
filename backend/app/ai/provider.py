from dataclasses import dataclass
from typing import Protocol


class AIProviderError(RuntimeError):
    """Raised when an external AI provider cannot complete a request."""


@dataclass(frozen=True, slots=True)
class AIAnswerResult:
    text: str
    model_name: str


class AIAnswerProvider(Protocol):
    @property
    def model_name(self) -> str:
        ...

    def generate_answer(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> AIAnswerResult:
        ...