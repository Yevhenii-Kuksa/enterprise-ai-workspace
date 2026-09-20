from typing import Any

import pytest
from app.core.config import Settings
from pydantic import ValidationError

TEST_DATABASE_URL = "postgresql+psycopg://test:test@localhost/test"
PRODUCTION_DATABASE_URL = (
    "postgresql+psycopg://enterprise_ai:strong-password@db:5432/enterprise_ai"
)


def test_settings_accept_valid_reliability_configuration() -> None:
    settings = Settings(
        database_url=TEST_DATABASE_URL,
        embedding_dimensions=1536,
        ai_reliability_max_evidence_distance=0.35,
        ai_reliability_max_source_age_days=30,
    )

    assert settings.embedding_dimensions == 1536
    assert settings.ai_reliability_max_evidence_distance == 0.35
    assert settings.ai_reliability_max_source_age_days == 30


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("embedding_dimensions", 0),
        ("embedding_dimensions", -1),
        ("ai_reliability_max_evidence_distance", -0.01),
        ("ai_reliability_max_evidence_distance", 1.01),
        ("ai_reliability_max_source_age_days", 0),
        ("ai_reliability_max_source_age_days", -1),
    ],
)
def test_settings_reject_invalid_numeric_configuration(
    field_name: str,
    invalid_value: int | float,
) -> None:
    overrides: dict[str, Any] = {
        field_name: invalid_value,
    }

    with pytest.raises(ValidationError):
        Settings(
            database_url=TEST_DATABASE_URL,
            **overrides,
        )


def test_development_environment_allows_missing_openai_api_key() -> None:
    settings = Settings(
        database_url=TEST_DATABASE_URL,
        app_environment="development",
        openai_api_key=None,
    )

    assert settings.app_environment == "development"
    assert settings.openai_api_key is None


def test_production_environment_accepts_safe_configuration() -> None:
    settings = Settings(
        database_url=PRODUCTION_DATABASE_URL,
        app_environment="production",
        openai_api_key="sk-production-test-key",
    )

    assert settings.app_environment == "production"
    assert settings.openai_api_key is not None


def test_production_environment_requires_openai_api_key() -> None:
    with pytest.raises(
        ValidationError,
        match="OPENAI_API_KEY is required in production",
    ):
        Settings(
            database_url=PRODUCTION_DATABASE_URL,
            app_environment="production",
            openai_api_key=None,
        )


def test_production_environment_rejects_placeholder_database_credentials() -> None:
    with pytest.raises(
        ValidationError,
        match="DATABASE_URL contains an unsafe placeholder credential",
    ):
        Settings(
            database_url=(
                "postgresql+psycopg://enterprise_ai:"
                "change_me@db:5432/enterprise_ai"
            ),
            app_environment="production",
            openai_api_key="sk-production-test-key",
        )

def test_settings_accept_valid_openai_request_controls() -> None:
    settings = Settings(
        database_url=TEST_DATABASE_URL,
        openai_timeout_seconds=30.0,
        openai_max_retries=2,
    )

    assert settings.openai_timeout_seconds == 30.0
    assert settings.openai_max_retries == 2


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("openai_timeout_seconds", 0),
        ("openai_timeout_seconds", -1.0),
        ("openai_max_retries", -1),
        ("openai_max_retries", 6),
    ],
)
def test_settings_reject_invalid_openai_request_controls(
    field_name: str,
    invalid_value: int | float,
) -> None:
    overrides: dict[str, Any] = {
        field_name: invalid_value,
    }

    with pytest.raises(ValidationError):
        Settings(
            database_url=TEST_DATABASE_URL,
            **overrides,
        )