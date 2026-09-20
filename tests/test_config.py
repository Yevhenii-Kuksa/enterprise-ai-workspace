from typing import Any

import pytest
from app.core.config import Settings
from pydantic import ValidationError

TEST_DATABASE_URL = "postgresql+psycopg://test:test@localhost/test"


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