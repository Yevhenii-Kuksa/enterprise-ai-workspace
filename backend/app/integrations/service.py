from app.integrations.provider_registry import (
    ProviderNotRegisteredError,
    ProviderRegistry,
)
from app.integrations.registry import (
    IntegrationNotRegisteredError,
    IntegrationRegistry,
)
from app.integrations.schemas import IntegrationRecord


class IntegrationServiceError(Exception):
    pass


class IntegrationUnavailableError(IntegrationServiceError):
    pass


class IntegrationProviderUnavailableError(IntegrationServiceError):
    pass


class IntegrationSourceMismatchError(IntegrationServiceError):
    pass


class IntegrationService:
    def __init__(
        self,
        integrations: IntegrationRegistry,
        providers: ProviderRegistry,
    ) -> None:
        self.integrations = integrations
        self.providers = providers

    def fetch_records(
        self,
        *,
        integration_key: str,
    ) -> list[IntegrationRecord]:
        try:
            definition = self.integrations.get(
                integration_key
            )
        except IntegrationNotRegisteredError as exc:
            raise IntegrationUnavailableError(
                f"Integration is not available: {integration_key}"
            ) from exc

        if not definition.enabled:
            raise IntegrationUnavailableError(
                f"Integration is disabled: {integration_key}"
            )

        try:
            provider = self.providers.get(
                integration_key
            )
        except ProviderNotRegisteredError as exc:
            raise IntegrationProviderUnavailableError(
                f"Provider is not available: {integration_key}"
            ) from exc

        records = list(
            provider.fetch_records()
        )

        for record in records:
            if record.source_system != integration_key:
                raise IntegrationSourceMismatchError(
                    "Integration record source does not match "
                    "the requested integration."
                )

        return records