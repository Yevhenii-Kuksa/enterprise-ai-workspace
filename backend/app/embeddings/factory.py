from app.core.config import Settings
from app.embeddings.openai_provider import OpenAIEmbeddingProvider
from app.embeddings.provider import EmbeddingProvider


def create_embedding_provider(
    settings: Settings,
) -> EmbeddingProvider:
    if settings.embedding_provider == "openai":
        if settings.openai_api_key is None:
            raise ValueError(
                "OPENAI_API_KEY is required for the OpenAI embedding provider."
            )

        return OpenAIEmbeddingProvider(
            api_key=settings.openai_api_key.get_secret_value(),
            model_name=settings.embedding_model,
            dimensions=settings.embedding_dimensions,
        )

    raise ValueError(
        f"Unsupported embedding provider: {settings.embedding_provider}"
    )