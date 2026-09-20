from app.ai.openai_provider import OpenAIAnswerProvider
from app.ai.provider import AIAnswerProvider
from app.core.config import Settings


def create_ai_answer_provider(
    settings: Settings,
) -> AIAnswerProvider:
    if settings.ai_answer_provider == "openai":
        if settings.openai_api_key is None:
            raise ValueError(
                "OPENAI_API_KEY is required for the OpenAI answer provider."
            )

        return OpenAIAnswerProvider(
            api_key=settings.openai_api_key.get_secret_value(),
            model_name=settings.ai_answer_model,
            timeout_seconds=settings.openai_timeout_seconds,
            max_retries=settings.openai_max_retries,
        )

    raise ValueError(
        f"Unsupported AI answer provider: {settings.ai_answer_provider}"
    )