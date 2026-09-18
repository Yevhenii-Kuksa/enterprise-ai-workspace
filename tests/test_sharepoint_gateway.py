from typing import Any

from app.integrations.sharepoint_gateway import (
    SharePointApiGateway,
)


class FakeGraphClient:
    def __init__(self) -> None:
        self.requested_path: str | None = None

    def get(
        self,
        path: str,
    ) -> dict[str, Any]:
        self.requested_path = path

        return {
            "value": [
                {
                    "id": "sp-file-001",
                    "name": "Instrukcja BHP.pdf",
                    "file": {
                        "mimeType": "application/pdf",
                    },
                }
            ]
        }


def test_sharepoint_gateway_lists_items() -> None:
    client = FakeGraphClient()

    gateway = SharePointApiGateway(
        client=client,
        drive_id="drive-001",
    )

    items = gateway.list_items(
        page_size=25,
    )

    assert len(items) == 1
    assert items[0]["id"] == "sp-file-001"

    assert client.requested_path == (
        "/drives/drive-001/root/children?$top=25"
    )