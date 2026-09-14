from openai import OpenAI

from app.ai.provider import AIAnswerResult


class OpenAIAnswerProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
    ) -> None:
        if not api_key:
            raise ValueError("OpenAI API key must not be empty.")

        if not model_name:
            raise ValueError("AI answer model name must not be empty.")

        self._model_name = model_name
        self._client = OpenAI(api_key=api_key)

    @property
    def model_name(self) -> str:
        return self._model_name

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