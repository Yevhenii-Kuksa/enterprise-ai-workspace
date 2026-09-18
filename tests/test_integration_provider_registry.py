from datetime import UTC, datetime

import pytest
from app.integrations.provider_registry import (
    ProviderAlreadyRegisteredError,
    ProviderNotRegisteredError,
    ProviderRegistry,
)
from app.integrations.schemas import IntegrationRecord


class FakeProvider:
    def fetch_records(
        self,
    ) -> list[IntegrationRecord]:
        return [
            IntegrationRecord(
                source_system="demo",
                external_id="record-001",
                record_type="document",
                payload={},
                fetched_at=datetime.now(UTC),
            )
        ]


def test_provider_registry_registers_provider() -> None:
    registry = ProviderRegistry()
    provider = FakeProvider()

    registry.register(
        "demo",
        provider,
    )

    assert registry.contains("demo") is True
    assert registry.get("demo") is provider


def test_provider_registry_rejects_duplicate_key() -> None:
    registry = ProviderRegistry()

    registry.register(
        "demo",
        FakeProvider(),
    )

    with pytest.raises(
        ProviderAlreadyRegisteredError
    ):
        registry.register(
            "demo",
            FakeProvider(),
        )


def test_provider_registry_rejects_unknown_provider() -> None:
    registry = ProviderRegistry()

    with pytest.raises(
        ProviderNotRegisteredError
    ):
        registry.get("missing")


def test_provider_registry_rejects_blank_key() -> None:
    registry = ProviderRegistry()

    with pytest.raises(ValueError):
        registry.register(
            "   ",
            FakeProvider(),
        )