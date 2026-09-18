import pytest
from app.integrations.sharepoint_client import (
    SharePointReadOnlyClient,
)


class FakeSharePointGateway:
    def __init__(self) -> None:
        self.requested_page_size: int | None = None

    def list_items(
        self,
        *,
        page_size: int,
    ) -> list[dict[str, object]]:
        self.requested_page_size = page_size

        return [
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
            },
            {
                "id": "folder-001",
                "name": "Procedury",
                "folder": {
                    "childCount": 5,
                },
            },
        ]


def test_sharepoint_read_only_client_fetches_only_files() -> None:
    gateway = FakeSharePointGateway()

    client = SharePointReadOnlyClient(
        gateway=gateway,
        page_size=25,
    )

    files = client.list_files()

    assert gateway.requested_page_size == 25

    assert len(files) == 1

    assert files[0].file_id == "sp-file-001"
    assert files[0].name == "Instrukcja BHP.pdf"
    assert files[0].mime_type == "application/pdf"


def test_sharepoint_read_only_client_rejects_invalid_page_size() -> None:
    with pytest.raises(ValueError):
        SharePointReadOnlyClient(
            gateway=FakeSharePointGateway(),
            page_size=0,
        )