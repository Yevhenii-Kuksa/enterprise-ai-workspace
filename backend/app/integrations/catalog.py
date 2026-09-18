from app.integrations.api_schemas import IntegrationSummaryResponse
from app.integrations.provider_registry import ProviderRegistry
from app.integrations.registry import IntegrationRegistry
from app.integrations.schemas import IntegrationStatus


class IntegrationCatalog:
    def __init__(
        self,
        *,
        integrations: IntegrationRegistry,
        providers: ProviderRegistry,
    ) -> None:
        self.integrations = integrations
        self.providers = providers

    def list_integrations(
        self,
    ) -> list[IntegrationSummaryResponse]:
        return [
            self._build_summary(definition.key)
            for definition in self.integrations.list_integrations()
        ]

    def _build_summary(
        self,
        integration_key: str,
    ) -> IntegrationSummaryResponse:
        definition = self.integrations.get(
            integration_key
        )

        if not definition.enabled:
            status = IntegrationStatus.DISABLED
        elif self.providers.contains(
            integration_key
        ):
            status = IntegrationStatus.READY
        else:
            status = IntegrationStatus.DEGRADED

        return IntegrationSummaryResponse(
            key=definition.key,
            kind=definition.kind,
            provider=definition.provider,
            capabilities=definition.capabilities,
            enabled=definition.enabled,
            status=status,
        )