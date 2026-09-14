from app.ai.factory import create_ai_answer_provider
from app.ai.openai_provider import OpenAIAnswerProvider
from app.core.config import Settings
from pydantic import SecretStr


def test_create_ai_answer_provider_requires_openai_api_key() -> None:
    settings = Settings(
        database_url="postgresql+psycopg://test:test@localhost/test",
        ai_answer_provider="openai",
        ai_answer_model="test-answer-model",
        openai_api_key=None,
    )

    try:
        create_ai_answer_provider(settings)
    except ValueError as exc:
        assert str(exc) == (
            "OPENAI_API_KEY is required for the OpenAI answer provider."
        )
    else:
        raise AssertionError("Expected ValueError.")


def test_create_ai_answer_provider_returns_openai_provider() -> None:
    settings = Settings(
        database_url="postgresql+psycopg://test:test@localhost/test",
        ai_answer_provider="openai",
        ai_answer_model="test-answer-model",
        openai_api_key=SecretStr("test-key"),
    )

    provider = create_ai_answer_provider(settings)

    assert isinstance(provider, OpenAIAnswerProvider)


def test_create_ai_answer_provider_uses_model_from_settings() -> None:
    settings = Settings(
        database_url="postgresql+psycopg://test:test@localhost/test",
        ai_answer_provider="openai",
        ai_answer_model="custom-answer-model",
        openai_api_key=SecretStr("test-key"),
    )

    provider = create_ai_answer_provider(settings)

    assert provider.model_name == "custom-answer-model"