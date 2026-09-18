import pytest
from app.integrations.google_drive_client import (
    GoogleDriveReadOnlyClient,
)


class FakeGoogleDriveGateway:
    def __init__(self) -> None:
        self.requested_page_size: int | None = None

    def list_files(
        self,
        *,
        page_size: int,
    ) -> list[dict[str, object]]:
        self.requested_page_size = page_size

        return [
            {
                "id": "file-001",
                "name": "Procedura magazynowa.pdf",
                "mimeType": "application/pdf",
                "modifiedTime": "2026-09-18T12:00:00Z",
            },
            {
                "id": "file-002",
                "name": "Cennik.xlsx",
                "mimeType": (
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                "modifiedTime": "2026-09-18T13:00:00Z",
            },
        ]


def test_google_drive_read_only_client_fetches_files() -> None:
    gateway = FakeGoogleDriveGateway()

    client = GoogleDriveReadOnlyClient(
        gateway=gateway,
        page_size=25,
    )

    files = client.list_files()

    assert gateway.requested_page_size == 25

    assert len(files) == 2

    assert files[0].file_id == "file-001"
    assert files[0].name == "Procedura magazynowa.pdf"

    assert files[1].file_id == "file-002"
    assert files[1].name == "Cennik.xlsx"


def test_google_drive_read_only_client_rejects_invalid_page_size() -> None:
    with pytest.raises(ValueError):
        GoogleDriveReadOnlyClient(
            gateway=FakeGoogleDriveGateway(),
            page_size=0,
        )