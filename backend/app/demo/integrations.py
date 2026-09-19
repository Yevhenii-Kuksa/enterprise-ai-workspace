from dataclasses import dataclass
from enum import StrEnum


class DemoIntegrationKind(StrEnum):
    EMAIL = "EMAIL"
    FILE_STORAGE = "FILE_STORAGE"
    CALENDAR = "CALENDAR"
    ERP = "ERP"


class DemoIntegrationStatus(StrEnum):
    READY = "READY"
    DEGRADED = "DEGRADED"


@dataclass(frozen=True, slots=True)
class DemoIntegration:
    integration_key: str
    name: str
    kind: DemoIntegrationKind
    status: DemoIntegrationStatus
    provider: str
    description: str
    capabilities: tuple[str, ...]


NEXALVORA_INTEGRATIONS = (
    DemoIntegration(
        integration_key="gmail",
        name="Gmail",
        kind=DemoIntegrationKind.EMAIL,
        status=DemoIntegrationStatus.READY,
        provider="Google Workspace",
        description=(
            "Skrzynka pocztowa wykorzystywana do komunikacji "
            "z dostawcami i klientami."
        ),
        capabilities=("READ_MESSAGES",),
    ),
    DemoIntegration(
        integration_key="google-drive",
        name="Google Drive",
        kind=DemoIntegrationKind.FILE_STORAGE,
        status=DemoIntegrationStatus.READY,
        provider="Google Workspace",
        description=(
            "Dokumentacja operacyjna, handlowa i techniczna Nexalvora."
        ),
        capabilities=("READ_FILES",),
    ),
    DemoIntegration(
        integration_key="sharepoint",
        name="SharePoint",
        kind=DemoIntegrationKind.FILE_STORAGE,
        status=DemoIntegrationStatus.READY,
        provider="Microsoft 365",
        description=(
            "Kontrolowana dokumentacja jakościowa i procedury firmowe."
        ),
        capabilities=("READ_FILES",),
    ),
    DemoIntegration(
        integration_key="google-calendar",
        name="Google Calendar",
        kind=DemoIntegrationKind.CALENDAR,
        status=DemoIntegrationStatus.READY,
        provider="Google Workspace",
        description=(
            "Spotkania operacyjne, odbiory materiałów "
            "i terminy związane z realizacją zamówień."
        ),
        capabilities=("READ_CALENDAR_EVENTS",),
    ),
    DemoIntegration(
        integration_key="erp",
        name="ERP",
        kind=DemoIntegrationKind.ERP,
        status=DemoIntegrationStatus.READY,
        provider="Nexalvora ERP",
        description=(
            "Zamówienia klientów, stany magazynowe "
            "i dane operacyjne wykorzystywane przez Workspace."
        ),
        capabilities=("READ_ERP_DATA",),
    ),
)