from app.core.config import Settings
from app.embeddings.factory import create_embedding_provider
from app.embeddings.openai_provider import OpenAIEmbeddingProvider
from pydantic import SecretStr


def test_create_embedding_provider_requires_openai_api_key() -> None:
    settings = Settings(
        database_url="postgresql+psycopg://test:test@localhost/test",
        embedding_provider="openai",
        embedding_model="test-model",
        embedding_dimensions=3,
        openai_api_key=None,
    )

    try:
        create_embedding_provider(settings)
    except ValueError as exc:
        assert str(exc) == (
            "OPENAI_API_KEY is required for the OpenAI embedding provider."
        )
    else:
        raise AssertionError("Expected ValueError.")


def test_create_embedding_provider_returns_openai_provider() -> None:
    settings = Settings(
        database_url="postgresql+psycopg://test:test@localhost/test",
        embedding_provider="openai",
        embedding_model="test-model",
        embedding_dimensions=3,
        openai_api_key=SecretStr("test-key"),
    )

    provider = create_embedding_provider(settings)

    assert isinstance(provider, OpenAIEmbeddingProvider)


def test_create_embedding_provider_uses_model_and_dimensions_from_settings() -> None:
    settings = Settings(
        database_url="postgresql+psycopg://test:test@localhost/test",
        embedding_provider="openai",
        embedding_model="custom-embedding-model",
        embedding_dimensions=1536,
        openai_api_key=SecretStr("test-key"),
    )

    provider = create_embedding_provider(settings)

    assert provider.model_name == "custom-embedding-model"
    assert provider.dimensions == 1536