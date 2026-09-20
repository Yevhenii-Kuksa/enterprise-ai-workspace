from openai import OpenAI

from app.ai.provider import AIAnswerResult


class OpenAIAnswerProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        timeout_seconds: float = 30.0,
        max_retries: int = 2,
    ) -> None:
        if not api_key:
            raise ValueError("OpenAI API key must not be empty.")

        if not model_name:
            raise ValueError("AI answer model name must not be empty.")

        if timeout_seconds <= 0:
            raise ValueError("OpenAI timeout must be greater than zero.")

        if max_retries < 0 or max_retries > 5:
            raise ValueError("OpenAI max retries must be between 0 and 5.")

        self._model_name = model_name
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
    def timeout_seconds(self) -> float:
        return self._timeout_seconds

    @property
    def max_retries(self) -> int:
        return self._max_retries

    def generate_answer(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> AIAnswerResult:
        response = self._client.responses.create(
            model=self._model_name,
            instructions=system_prompt,
            input=user_prompt,
        )

        return AIAnswerResult(
            text=response.output_text,
            model_name=self._model_name,
        )