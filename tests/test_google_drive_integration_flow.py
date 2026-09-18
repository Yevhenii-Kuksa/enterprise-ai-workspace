from typing import Any

from app.integrations.file_storage import FileStorageProvider
from app.integrations.google_drive_client import GoogleDriveReadOnlyClient
from app.integrations.google_drive_gateway import GoogleDriveApiGateway
from app.integrations.provider_registry import ProviderRegistry
from app.integrations.registry import IntegrationRegistry
from app.integrations.schemas import (
    IntegrationCapability,
    IntegrationDefinition,
    IntegrationKind,
)
from app.integrations.service import IntegrationService


class FakeRequest:
    def __init__(
        self,
        response: dict[str, Any],
    ) -> None:
        self.response = response

    def execute(
        self,
    ) -> dict[str, Any]:
        return self.response


class FakeFilesResource:
    def list(
        self,
        **kwargs: Any,
    ) -> FakeRequest:
        return FakeRequest(
            {
                "files": [
                    {
                        "id": "file-001",
                        "name": "Procedura magazynowa.pdf",
                        "mimeType": "application/pdf",
                        "modifiedTime": "2026-09-18T12:00:00Z",
                        "driveId": "drive-001",
                        "webViewLink": (
                            "https://drive.google.com/"
                            "file/d/file-001/view"
                        ),
                    }
                ]
            }
        )


class FakeGoogleDriveService:
    def __init__(self) -> None:
        self._files = FakeFilesResource()

    def files(
        self,
    ) -> FakeFilesResource:
        return self._files


def test_google_drive_end_to_end_integration_flow() -> None:
    gateway = GoogleDriveApiGateway(
        service=FakeGoogleDriveService(),
    )

    client = GoogleDriveReadOnlyClient(
        gateway=gateway,
        page_size=10,
    )

    provider = FileStorageProvider(
        source_system="google-drive",
        client=client,
    )

    integration_registry = IntegrationRegistry(
        [
            IntegrationDefinition(
                key="google-drive",
                kind=IntegrationKind.FILE_STORAGE,
                provider="google",
                capabilities=(
                    IntegrationCapability.READ_FILES,
                ),
            )
        ]
    )

    provider_registry = ProviderRegistry()
    provider_registry.register(
        "google-drive",
        provider,
    )

    service = IntegrationService(
        integration_registry,
        provider_registry,
    )

    records = service.fetch_records(
        integration_key="google-drive",
    )

    assert len(records) == 1

    record = records[0]

    assert record.source_system == "google-drive"
    assert record.external_id == "file-001"
    assert record.record_type == "file"

    assert record.payload["name"] == "Procedura magazynowa.pdf"
    assert record.payload["mime_type"] == "application/pdf"