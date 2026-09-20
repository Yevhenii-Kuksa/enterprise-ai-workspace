from dataclasses import dataclass

from app.ai.openai_provider import OpenAIAnswerProvider


@dataclass
class FakeResponse:
    output_text: str


class FakeResponsesClient:
    def __init__(
        self,
        response: FakeResponse,
    ) -> None:
        self._response = response
        self.calls: list[dict[str, str]] = []

    def create(
        self,
        *,
        model: str,
        instructions: str,
        input: str,
    ) -> FakeResponse:
        self.calls.append(
            {
                "model": model,
                "instructions": instructions,
                "input": input,
            }
        )

        return self._response


class FakeOpenAIClient:
    def __init__(
        self,
        response: FakeResponse,
    ) -> None:
        self.responses = FakeResponsesClient(response)


def test_openai_answer_provider_rejects_empty_api_key() -> None:
    try:
        OpenAIAnswerProvider(
            api_key="",
            model_name="test-model",
        )
    except ValueError as exc:
        assert str(exc) == "OpenAI API key must not be empty."
    else:
        raise AssertionError("Expected ValueError.")


def test_openai_answer_provider_rejects_empty_model_name() -> None:
    try:
        OpenAIAnswerProvider(
            api_key="test-key",
            model_name="",
        )
    except ValueError as exc:
        assert str(exc) == "AI answer model name must not be empty."
    else:
        raise AssertionError("Expected ValueError.")


def test_openai_answer_provider_generates_answer() -> None:
    provider = OpenAIAnswerProvider(
        api_key="test-key",
        model_name="test-answer-model",
    )

    fake_client = FakeOpenAIClient(
        FakeResponse(
            output_text="Odpowiedź oparta na źródle [S1].",
        )
    )

    provider._client = fake_client  # type: ignore[assignment]

    result = provider.generate_answer(
        system_prompt="Odpowiadaj tylko na podstawie źródeł.",
        user_prompt="Jak przyjąć towar?",
    )

    assert result.text == "Odpowiedź oparta na źródle [S1]."
    assert result.model_name == "test-answer-model"

    assert fake_client.responses.calls == [
        {
            "model": "test-answer-model",
            "instructions": "Odpowiadaj tylko na podstawie źródeł.",
            "input": "Jak przyjąć towar?",
        }
    ]

def test_openai_answer_provider_exposes_request_controls() -> None:
    provider = OpenAIAnswerProvider(
        api_key="test-key",
        model_name="test-model",
        timeout_seconds=15.0,
        max_retries=3,
    )

    assert provider.timeout_seconds == 15.0
    assert provider.max_retries == 3


def test_openai_answer_provider_rejects_invalid_timeout() -> None:
    try:
        OpenAIAnswerProvider(
            api_key="test-key",
            model_name="test-model",
            timeout_seconds=0,
        )
    except ValueError as exc:
        assert str(exc) == "OpenAI timeout must be greater than zero."
    else:
        raise AssertionError("Expected ValueError.")


def test_openai_answer_provider_rejects_invalid_max_retries() -> None:
    try:
        OpenAIAnswerProvider(
            api_key="test-key",
            model_name="test-model",
            max_retries=6,
        )
    except ValueError as exc:
        assert str(exc) == "OpenAI max retries must be between 0 and 5."
    else:
        raise AssertionError("Expected ValueError.")