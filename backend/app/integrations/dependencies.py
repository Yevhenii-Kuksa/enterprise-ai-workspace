from app.integrations.catalog import IntegrationCatalog
from app.integrations.provider_registry import ProviderRegistry
from app.integrations.registry import IntegrationRegistry
from app.integrations.schemas import (
    IntegrationCapability,
    IntegrationDefinition,
    IntegrationKind,
)
from app.integrations.service import IntegrationService

integration_registry = IntegrationRegistry(
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
            key="google-drive",
            kind=IntegrationKind.FILE_STORAGE,
            provider="google",
            capabilities=(
                IntegrationCapability.READ_FILES,
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
            key="google-calendar",
            kind=IntegrationKind.CALENDAR,
            provider="google",
            capabilities=(
                IntegrationCapability.READ_CALENDAR_EVENTS,
            ),
        ),
        IntegrationDefinition(
            key="erp",
            kind=IntegrationKind.ERP,
            provider="internal",
            capabilities=(
                IntegrationCapability.READ_ERP_DATA,
            ),
        ),
    ]
)

integration_provider_registry = ProviderRegistry()


def get_integration_catalog() -> IntegrationCatalog:
    return IntegrationCatalog(
        integrations=integration_registry,
        providers=integration_provider_registry,
    )


def get_integration_service() -> IntegrationService:
    return IntegrationService(
        integration_registry,
        integration_provider_registry,
    )