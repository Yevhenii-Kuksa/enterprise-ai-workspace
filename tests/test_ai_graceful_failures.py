import uuid
from unittest.mock import patch

import pytest
from app.ai.openai_provider import OpenAIAnswerProvider
from app.ai.provider import AIProviderError
from app.core.config import Settings, get_settings
from app.db.dependencies import get_db
from app.embeddings.openai_provider import OpenAIEmbeddingProvider
from app.embeddings.provider import EmbeddingProviderError
from app.main import app
from app.security.current_user import CurrentUser
from app.security.dependencies import get_current_user
from fastapi.testclient import TestClient


class FailingResponses:
    def create(self, **_: object) -> object:
        raise ConnectionError("Synthetic OpenAI answer failure.")


class FailingAnswerClient:
    def __init__(self) -> None:
        self.responses = FailingResponses()


class FailingEmbeddings:
    def create(self, **_: object) -> object:
        raise TimeoutError("Synthetic OpenAI embedding failure.")


class FailingEmbeddingClient:
    def __init__(self) -> None:
        self.embeddings = FailingEmbeddings()


class FakeDb:
    pass


def _current_user() -> CurrentUser:
    return CurrentUser(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        department_id=uuid.uuid4(),
        is_active=True,
        permissions=set(),
    )


def _settings() -> Settings:
    return Settings(
        database_url="postgresql://test",
        openai_api_key="test-api-key",
    )


def test_openai_answer_provider_normalizes_external_failure() -> None:
    provider = OpenAIAnswerProvider(
        api_key="test-key",
        model_name="test-model",
    )
    provider._client = FailingAnswerClient()  # type: ignore[assignment]

    with pytest.raises(
        AIProviderError,
        match="AI answer provider request failed.",
    ):
        provider.generate_answer(
            system_prompt="System",
            user_prompt="User",
        )


def test_openai_embedding_provider_normalizes_external_failure() -> None:
    provider = OpenAIEmbeddingProvider(
        api_key="test-key",
        model_name="test-model",
        dimensions=3,
    )
    provider._client = FailingEmbeddingClient()  # type: ignore[assignment]

    with pytest.raises(
        EmbeddingProviderError,
        match="Embedding provider request failed.",
    ):
        provider.embed_texts(
            ["test"],
        )


@pytest.mark.parametrize(
    "provider_error",
    [
        AIProviderError("Internal AI provider detail."),
        EmbeddingProviderError("Internal embedding provider detail."),
    ],
)
def test_rag_api_maps_provider_failure_to_safe_503(
    provider_error: RuntimeError,
) -> None:
    app.dependency_overrides[get_db] = lambda: FakeDb()
    app.dependency_overrides[get_current_user] = _current_user
    app.dependency_overrides[get_settings] = _settings

    try:
        with patch(
            "app.api.rag.answer_rag_query_from_settings",
            side_effect=provider_error,
        ):
            client = TestClient(app)

            response = client.post(
                "/api/rag/query",
                json={
                    "query": "Jaki jest status zamówienia?",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {
        "detail": "AI service is temporarily unavailable."
    }

    response_body = response.text

    assert "Internal AI provider detail." not in response_body
    assert "Internal embedding provider detail." not in response_body