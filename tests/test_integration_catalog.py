from app.integrations.catalog import IntegrationCatalog
from app.integrations.provider_registry import ProviderRegistry
from app.integrations.registry import IntegrationRegistry
from app.integrations.schemas import (
    IntegrationCapability,
    IntegrationDefinition,
    IntegrationKind,
    IntegrationRecord,
    IntegrationStatus,
)


class FakeProvider:
    def fetch_records(
        self,
    ) -> list[IntegrationRecord]:
        return []


def test_integration_catalog_reports_runtime_status() -> None:
    integrations = IntegrationRegistry(
        [
            IntegrationDefinition(
                key="gmail",
                kind=IntegrationKind.EMAIL,
                provider="google",
                capabilities=(
                    IntegrationCapability.READ_MESSAGES,
                ),
            ),
            IntegrationDefinition(
                key="sharepoint",
                kind=IntegrationKind.FILE_STORAGE,
                provider="microsoft",
                capabilities=(
                    IntegrationCapability.READ_FILES,
                ),
            ),
            IntegrationDefinition(
                key="calendar-disabled",
                kind=IntegrationKind.CALENDAR,
                provider="google",
                capabilities=(
                    IntegrationCapability.READ_CALENDAR_EVENTS,
                ),
                enabled=False,
            ),
        ]
    )

    providers = ProviderRegistry()
    providers.register(
        "gmail",
        FakeProvider(),
    )

    catalog = IntegrationCatalog(
        integrations=integrations,
        providers=providers,
    )

    results = catalog.list_integrations()

    assert len(results) == 3

    by_key = {
        result.key: result
        for result in results
    }

    assert by_key["gmail"].status == IntegrationStatus.READY

    assert (
        by_key["sharepoint"].status
        == IntegrationStatus.DEGRADED
    )

    assert (
        by_key["calendar-disabled"].status
        == IntegrationStatus.DISABLED
    )