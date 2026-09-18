from datetime import UTC, datetime

import pytest
from app.integrations.provider_registry import ProviderRegistry
from app.integrations.registry import IntegrationRegistry
from app.integrations.schemas import (
    IntegrationCapability,
    IntegrationDefinition,
    IntegrationKind,
    IntegrationRecord,
)
from app.integrations.service import (
    IntegrationProviderUnavailableError,
    IntegrationService,
    IntegrationSourceMismatchError,
    IntegrationUnavailableError,
)


class FakeProvider:
    def __init__(
        self,
        source_system: str = "google-drive",
    ) -> None:
        self.source_system = source_system

    def fetch_records(
        self,
    ) -> list[IntegrationRecord]:
        return [
            IntegrationRecord(
                source_system=self.source_system,
                external_id="file-001",
                record_type="document",
                payload={
                    "name": "Procedura magazynowa.pdf",
                },
                fetched_at=datetime.now(UTC),
            )
        ]


def definition(
    *,
    enabled: bool = True,
) -> IntegrationDefinition:
    return IntegrationDefinition(
        key="google-drive",
        kind=IntegrationKind.FILE_STORAGE,
        provider="google",
        capabilities=(
            IntegrationCapability.READ_FILES,
        ),
        enabled=enabled,
    )


def test_service_fetches_records_from_registered_provider() -> None:
    integrations = IntegrationRegistry(
        [definition()]
    )

    providers = ProviderRegistry()
    providers.register(
        "google-drive",
        FakeProvider(),
    )

    service = IntegrationService(
        integrations,
        providers,
    )

    records = service.fetch_records(
        integration_key="google-drive",
    )

    assert len(records) == 1
    assert records[0].source_system == "google-drive"
    assert records[0].external_id == "file-001"


def test_service_rejects_unknown_integration() -> None:
    service = IntegrationService(
        IntegrationRegistry(),
        ProviderRegistry(),
    )

    with pytest.raises(
        IntegrationUnavailableError
    ):
        service.fetch_records(
            integration_key="missing",
        )


def test_service_rejects_disabled_integration() -> None:
    service = IntegrationService(
        IntegrationRegistry(
            [definition(enabled=False)]
        ),
        ProviderRegistry(),
    )

    with pytest.raises(
        IntegrationUnavailableError
    ):
        service.fetch_records(
            integration_key="google-drive",
        )


def test_service_rejects_missing_provider() -> None:
    service = IntegrationService(
        IntegrationRegistry(
            [definition()]
        ),
        ProviderRegistry(),
    )

    with pytest.raises(
        IntegrationProviderUnavailableError
    ):
        service.fetch_records(
            integration_key="google-drive",
        )


def test_service_rejects_source_mismatch() -> None:
    integrations = IntegrationRegistry(
        [definition()]
    )

    providers = ProviderRegistry()
    providers.register(
        "google-drive",
        FakeProvider(
            source_system="sharepoint",
        ),
    )

    service = IntegrationService(
        integrations,
        providers,
    )

    with pytest.raises(
        IntegrationSourceMismatchError
    ):
        service.fetch_records(
            integration_key="google-drive",
        )