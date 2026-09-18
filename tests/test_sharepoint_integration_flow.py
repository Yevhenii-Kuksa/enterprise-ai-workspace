from typing import Any

from app.integrations.file_storage import FileStorageProvider
from app.integrations.provider_registry import ProviderRegistry
from app.integrations.registry import IntegrationRegistry
from app.integrations.schemas import (
    IntegrationCapability,
    IntegrationDefinition,
    IntegrationKind,
)
from app.integrations.service import IntegrationService
from app.integrations.sharepoint_client import SharePointReadOnlyClient
from app.integrations.sharepoint_gateway import SharePointApiGateway


class FakeGraphClient:
    def get(
        self,
        path: str,
    ) -> dict[str, Any]:
        return {
            "value": [
                {
                    "id": "sp-file-001",
                    "name": "Instrukcja BHP.pdf",
                    "lastModifiedDateTime": (
                        "2026-09-18T14:00:00Z"
                    ),
                    "webUrl": (
                        "https://nexalvora.sharepoint.com/"
                        "documents/sp-file-001"
                    ),
                    "file": {
                        "mimeType": "application/pdf",
                    },
                    "parentReference": {
                        "driveId": "drive-001",
                        "path": (
                            "/drives/drive-001/root:/Procedury"
                        ),
                    },
                }
            ]
        }


def test_sharepoint_end_to_end_integration_flow() -> None:
    gateway = SharePointApiGateway(
        client=FakeGraphClient(),
        drive_id="drive-001",
    )

    client = SharePointReadOnlyClient(
        gateway=gateway,
        page_size=10,
    )

    provider = FileStorageProvider(
        source_system="sharepoint",
        client=client,
    )

    integration_registry = IntegrationRegistry(
        [
            IntegrationDefinition(
                key="sharepoint",
                kind=IntegrationKind.FILE_STORAGE,
                provider="microsoft",
                capabilities=(
                    IntegrationCapability.READ_FILES,
                ),
            )
        ]
    )

    provider_registry = ProviderRegistry()
    provider_registry.register(
        "sharepoint",
        provider,
    )

    service = IntegrationService(
        integration_registry,
        provider_registry,
    )

    records = service.fetch_records(
        integration_key="sharepoint",
    )

    assert len(records) == 1

    record = records[0]

    assert record.source_system == "sharepoint"
    assert record.external_id == "sp-file-001"
    assert record.record_type == "file"

    assert record.payload["name"] == "Instrukcja BHP.pdf"
    assert record.payload["mime_type"] == "application/pdf"